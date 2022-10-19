"""
测试集结果
"""
import os
import argparse
import shutil
from pathlib import Path
import cv2
import numpy as np
from easydict import EasyDict
from PIL import Image
from utils import datasets, detect_utils, torch_utils, general
import torch
from models import resnet_zoo, resnet_zoo_half, resnet_zoo_behavior
import yaml
import damei as dm


def detect(opt):
	# 设置
	cuda = opt.device != 'cpu'
	device_id = [int(x) for x in opt.device.split(',')] if cuda else None
	torch_device = torch_utils.select_device(device=opt.device, batch_size=opt.batch_size)

	# 加载模型
	classes = opt.cfg['statuses']
	nc = len(classes)

	test_paths = [f'{opt.source}/{x}' for x in os.listdir(opt.source) if os.path.isdir(f'{opt.source}/{x}')]
	test_loader = datasets.StatusDataLoader(balance=False, dformat='behavior').get_loader(
		trte_path=test_paths, batch_size=opt.batch_size, cfg=opt.cfg)
	model = resnet_zoo_behavior.attempt_load(model_name='resnet50', pretrained=False, num_classes=nc)

	# optimizer = torch.optim.SGD(model.parameters(), hyp['lr0'], momentum=hyp['momentum'],
	# 							weight_decay=hyp['weight_decay'])
	optimizer = torch.optim.SGD(
		model.parameters(), opt.cfg['lr0'], momentum=opt.cfg['momentum'], weight_decay=opt.cfg['weight_decay'])

	model, optimizer, start_epoch = general.load_resume2(
		opt.weights, model, optimizer)

	# print(model)

	if cuda:
		model = model.to(torch_device)
		if torch.cuda.device_count() > 1:
			model = torch.nn.DataParallel(model, device_ids=device_id)

	if opt.output is not None:
		tp = opt.output  # target path
		if os.path.exists(tp):
			shutil.rmtree(tp)
		os.makedirs(tp)

	model.eval()
	stt = general.synchronize_time()
	confusion_matrix = np.zeros((nc, nc), dtype=np.int32)
	total_time = 0
	for i, (input, target, img_path, status) in enumerate(test_loader):
		test_start_time = general.synchronize_time()
		# print(input.shape)
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
			total_time += (general.synchronize_time() - test_start_time)
			P, R, F1, acc = dm.general.confusion2score(confusion_matrix)
			val_ret = \
				f'\rTest [{i + 1:>3}/{len(test_loader):>3}] {"":>14} ' \
				f'mean_F1: {np.mean(F1) * 100:>6.3f}% mean_acc: {acc * 100:>6.3f}% valid_time: {total_time:.4f}s'
			print(val_ret, end='')

		if opt.output is not None:
			txt_file = f'{tp}/{Path(stem).stem}.txt'
			with open(txt_file, 'w') as f:
				f.writelines([f'{ce}\n'])
	print('')
	general.plot_confusion_matrix(confusion_matrix, classes=classes)
	sstime = general.synchronize_time() - stt
	# ret = f'\nstatus: {status:<15} {correct} {error} {total} accuracy: {correct/total*100:.2f}% time: {sstime:.2f}s'
	# print(ret)
	# os.system(f'echo "{ret}" >> detect_result.txt')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--source', type=str, default='', help='source path')
	parser.add_argument('--cfg_file', type=str, default='data/cfg.yaml', help='hyperparamers path')
	parser.add_argument('--batch_size', type=int, default=8, help='total batch size')
	parser.add_argument('--weights', default=None, help='resume from given path/last.pt')
	parser.add_argument('--device', type=str, default='0', help='cuda device, i.e. 0,1,2,3 or cpu')
	parser.add_argument('--output', type=str, default=None, help='save img')

	opt = parser.parse_args()

	opt.weights = '/home/zzd/PycharmProject/pose/behavior/classifier/ResNet50/runs/300EPexp/weights/best.pt'
	opt.weights = '/home/zzd/PycharmProject/pose/behavior/classifier/ResNet50/runs/exp2/weights/best.pt'
	opt.source = '/home/zzd/datasets/ceyu/features_hcw3_only_skeleton_trteval/test'

	with open(opt.cfg_file, 'r') as f:
		opt.cfg = EasyDict(yaml.load(f, Loader=yaml.FullLoader))

	detect(opt)











