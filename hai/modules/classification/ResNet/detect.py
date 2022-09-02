"""
有模型之后，推算结果
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

	# 加载数据
	if isinstance(opt.source, str):
		sp = opt.source  # source path
		stems = [Path(x).stem for x in os.listdir(sp) if x.endswith(opt.suffix)]
	else:
		stems = opt.source

	tp = opt.output  # target path
	if os.path.exists(tp):
		shutil.rmtree(tp)
	os.makedirs(tp)
	assert len(stems) > 0
	target = statuses.index(status)
	# print(target)

	# 如果val_path不为None，就查看哪些是stem是val，只有是val的stem才预测
	if opt.val_path is not None:
		valstems = os.listdir(f'{opt.val_path}/{scene}')
		valstems = [Path(x).stem.split('_')[-1] for x in valstems if 'vis' in x]
		print(f'val stems: {len(valstems)}')
	else:
		valstems = stems

	correct = 0
	error = 0
	total = 0
	stems = sorted(stems)
	model.eval()
	stt = general.synchronize_time()
	for i, stem in enumerate(stems):
		if stem not in valstems:
			continue
		# img = detect_utils.load_vis_lidar_img_only(vis_sp, lidar_sp, stem, model_size=opt.img_size, suffix='png')
		# img = detect_utils.load_target_status_img_only(f'{sp}/{stem}{opt.suffix}')
		img_path = f'{sp}/{stem}{opt.suffix}' if isinstance(opt.source, str) else stem
		img = cv2.imread(img_path)
		img = np.array(img, dtype=np.float32)
		img = np.transpose(img/255.0, (2, 0, 1))  # [3, 256, 256]

		x = torch.from_numpy(img).unsqueeze(0)  # [1, 3, 256, 256]
		start_time = general.synchronize_time()
		output = model(x)
		output = output.cpu().detach().numpy()
		if target == np.argmax(output):
			correct += 1
			ce = f'correct {scene}'  # correct or error
		else:
			error += 1
			ce = f'error   {scene} --> {classes[np.argmax(output)]}'
		total += 1
		inference_time = general.synchronize_time() - start_time
		prt = \
			f'\r[{i+1:>4}/{len(stems):>4}] {correct:>4} {error:>4} acc: {correct/(correct+error)*100:.2f}% ' \
			f'inf_time: {inference_time:.5f}s {ce}'
		print(prt, end='')
		if opt.save:
			txt_file = f'{tp}/{Path(stem).stem}.txt'
			with open(txt_file, 'w') as f:
				f.writelines([f'{ce}\n'])
	sstime = general.synchronize_time() - stt
	ret = f'\nstatus: {status:<15} {correct} {error} {total} accuracy: {correct/total*100:.2f}% time: {sstime:.2f}s'
	print(ret)
	os.system(f'echo "{ret}" >> detect_result.txt')
	return correct, error


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--source', type=str, default='', help='source path')
	parser.add_argument('--cfg_file', type=str, default='data/cfg.yaml', help='hyperparamers path')
	parser.add_argument('--batch_size', type=int, default=8, help='total batch size')
	# parser.add_argument('--resume', default='runs/exp0/weights/last.pt', help='resume from given path/last.pt')
	parser.add_argument('--weights', default=None, help='resume from given path/last.pt')
	parser.add_argument('--device', type=str, default='0', help='cuda device, i.e. 0,1,2,3 or cpu')
	parser.add_argument('--save', type=bool, default=True, help='save img')
	opt = parser.parse_args()

	opt.weights = '/home/zzd/PycharmProject/pose/behavior/classifier/ResNet50/runs/300EPexp/weights/best.pt'
	opt.weights = '/home/zzd/PycharmProject/pose/behavior/classifier/ResNet50/runs/exp2/weights/best.pt'
	opt.source = '/home/zzd/datasets/ceyu/features_hcw3_only_skeleton_trteval/test'

	with open(opt.cfg_file, 'r') as f:
		opt.cfg = EasyDict(yaml.load(f, Loader=yaml.FullLoader))

	detect(opt)











