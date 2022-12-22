import sys
import os
import re
import torch
import torchvision
import torch.nn as nn
import argparse
import yaml, math
from easydict import EasyDict
from pathlib import Path
import numpy as np
import damei as dm
from hai.modules.classification.ResNet.models import resnet_arch
from utils import datasets, torch_utils, general, dm_control
from models import resnet_zoo_half, resnet_zoo_behavior


def train(opt):
	# 设置
	cuda = opt.device != 'cpu'
	device_id = [int(x) for x in opt.device.split(',')] if cuda else None
	torch_device = torch_utils.select_device(device=opt.device, batch_size=opt.batch_size)

	# 数据
	s = opt.source
	train_paths = [f'{s}/train/{x}' for x in os.listdir(f'{s}/train') if os.path.isdir(f'{s}/train/{x}')]
	val_paths = [f'{s}/val/{x}' for x in os.listdir(f'{s}/val') if os.path.isdir(f'{s}/val/{x}')]

	statuses = opt.cfg['statuses']
	nc = len(statuses)

	train_loader = datasets.StatusDataLoader(balance=opt.balance, dformat='behavior').get_loader(
		trte_path=train_paths, batch_size=opt.batch_size, cfg=opt.cfg)
	val_loader = datasets.StatusDataLoader(balance=opt.balance, dformat='behavior').get_loader(
		trte_path=val_paths, batch_size=opt.batch_size, cfg=opt.cfg)

	# model
	model = resnet_zoo_behavior.attempt_load(model_name='resnet50', pretrained=False, num_classes=nc)
	model.nc = nc
	# 损失函数、优化器和学习率控制器
	criterion = nn.CrossEntropyLoss()
	optimizer = torch.optim.SGD(
		model.parameters(), opt.cfg['lr0'], momentum=opt.cfg['momentum'], weight_decay=opt.cfg['weight_decay'])
	lf = lambda x: (((1 + math.cos(x * math.pi / opt.epochs)) / 2) ** 1.0) * 0.8 + 0.2  # cosine
	scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lf)

	if opt.resume is None:
		# lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.95)
		start_epoch = 0
	else:
		model, optimizer, scheduler, start_epoch = general.load_resume(
			opt.resume, model, optimizer, torch_device)

	if cuda:
		model = model.to(torch_device)
		if torch.cuda.device_count() > 1:
			model = torch.nn.DataParallel(model, device_ids=device_id)

	scheduler.last_epoch = start_epoch - 1
	last_acc = 0
	for epoch in range(start_epoch, opt.epochs):
		model.train()
		confusion_matrix = np.zeros((nc, nc), dtype=np.int32)
		total_loss = 0
		total_time = 0
		for i, (input, target, img_path, status) in enumerate(train_loader):
			start_time = general.synchronize_time()
			# print(input.shape, target, img_path, status)
			# with torch.no_grad():
			if True:
				input.requires_grad = True
				input = input.to(torch_device)
				target = target.to(torch_device)
				output = model(input)  # [8, 365]
				# output.requires_grad = True

			loss = criterion(output, target)
			total_loss += loss.data
			# measure accuracy
			output = torch.argmax(output, dim=1)  # [bs, ]
			for j in range(len(output)):
				m = int(target.cpu().numpy()[j])
				n = int(output.cpu().numpy()[j])
				confusion_matrix[m, n] += 1
			P, R, F1, acc = dm.general.confusion2score(confusion_matrix, round=5)
			# print(target, output, '\n', confusion_matrix, F1, acc)
			t = general.synchronize_time() - start_time
			total_time += t
			train_ret = \
				f"\rTraining   [{epoch+1:>3}/{opt.epochs}] [{i+1:>3}/{len(train_loader):>3}] loss: {total_loss/(i+1):>8.4f} " \
				f"mean_F1: {np.mean(F1)*100:>6.3f}% mean_acc: {acc*100:>6.3f}% batch_time: {total_time/(i+1):.4f}s "
			print(train_ret, end='')
			expc.echo_info(train_ret, opt.results_file)

			optimizer.zero_grad()
			loss.backward()
			optimizer.step()
			# break
		print('')
		scheduler.step()

		# validation
		confusion_matrix = np.zeros((nc, nc), dtype=np.int32)
		model.eval()
		total_time = 0
		for i, (input, target, img_path, statuses) in enumerate(val_loader):
			val_start_time = general.synchronize_time()
			with torch.no_grad():
				input.requires_grad = False
				input = input.to(torch_device)
				target = target.to(torch_device)
				output = model(input)  # [bs, nc]
				output = torch.argmax(output, dim=1)  # [bs, ]
				for j in range(len(output)):
					m = int(target.cpu().numpy()[j])
					n = int(output.cpu().numpy()[j])
					confusion_matrix[m, n] += 1
				# print(confusion_matrix)
				total_time += (general.synchronize_time() - val_start_time)
				P, R, F1, acc = dm.general.confusion2score(confusion_matrix)
				val_ret = \
					f'\rValidation [{epoch+1:>3}/{opt.epochs}] [{i+1:>3}/{len(val_loader):>3}] {"":>14} ' \
					f'mean_F1: {np.mean(F1)*100:>6.3f}% mean_acc: {acc*100:>6.3f}% valid_time: {total_time:.4f}s'
				print(val_ret, end='')
		# val_ret = f'{val_ret} '
		# print(val_ret)
		print(f'\n{" ".join(opt.cfg["statuses"])}, confusion matrix:')
		expc.echo_info(val_ret, txt=opt.results_file)
		plt_cm_str = general.plot_confusion_matrix(confusion_matrix, classes=opt.cfg['statuses'])
		expc.echo_info(plt_cm_str, txt=opt.results_file)

		# 保存模型
		if opt.save:
			final_epoch = epoch+1 == opt.epochs
			with open(f'{expc.exp_path}/{opt.results_file}', 'r') as f:
				result_data = f.readlines()

			ckpt = {
				'epoch': epoch + 1,
				'training_results': result_data,
				'model': model.module.state_dict() if hasattr(model, 'module') else model.state_dict(),
				'optimizer': None if final_epoch else optimizer.state_dict(),
				'classes': opt.cfg['statuses']}
			expc.save_model(ckpt, model_name='last.pt')

			if acc > last_acc:
				print(f'SOTA reached at epoch: {epoch+1}, ', end='')
				expc.save_model(ckpt, model_name='best.pt')
				last_acc = acc
				print('\n')


def accuracy(output, target, topk=(1,)):
	"""
	Computes the precision@k for the specified values of k
	"""
	maxk = max(topk)
	batch_size = target.size(0)
	# print(output.shape)
	# print(maxk, batch_size)

	_, pred = output.topk(maxk, 1, True, True)
	# print(pred)
	# print(target)
	pred = pred.t()
	correct = pred.eq(target.view(1, -1).expand_as(pred))
	# print(correct)

	res = torch.Tensor((len(topk)))
	res[:] = 0  # init
	for i, k in enumerate(topk):
		correct_k = correct[:k].contiguous().view(-1).float().sum(0)
		# res.append(correct_k.mul_(100.0 / batch_size))
		res[i] = correct_k.mul_(100.0 / batch_size)
	return res


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--source', type=str, default='', help='source path')
	parser.add_argument('--cfg_file', type=str, default='data/cfg.yaml', help='hyperparamers path')
	parser.add_argument('--epochs', type=int, default=300)
	parser.add_argument('--batch_size', type=int, default=8, help='total batch size')
	# parser.add_argument('--resume', default='runs/exp0/weights/last.pt', help='resume from given path/last.pt')
	parser.add_argument('--resume', default=None, help='resume from given path/last.pt')
	parser.add_argument('--device', type=str, default='0', help='cuda device, i.e. 0,1,2,3 or cpu')
	parser.add_argument('--save', type=bool, default=True, help='save trained model')
	parser.add_argument('--results_file', type=str, default='results.txt', help='store results')
	parser.add_argument('--balance', type=bool, default=False, help='balance train val sets')
	opt = parser.parse_args()

	expc = dm_control.DmExperimentControl()

	opt.source = '/home/zzd/datasets/ceyu/features_hcw3_only_skeleton_trteval'
	# opt.source = '/home/zzd/datasets/ceyu/features_hcw3_trteval'
	print(opt)
	# 获取hyp
	with open(opt.cfg_file, 'r') as f:
		opt.cfg = EasyDict(yaml.load(f, Loader=yaml.FullLoader))
	train(opt)

	# cm = np.random.randint(1, 100, size=(7, 7))
	# plot_confusion_matrix(cm)


