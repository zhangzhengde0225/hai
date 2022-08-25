import torch
import time
import numpy as np
import cv2
import damei as dm


def synchronize_time():
	torch.cuda.synchronize() if torch.cuda.is_available() else None
	return time.time()


def load_weights(weights_path, model, device=None, need_ckpt=False):
	device = device if device is not None else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
	ckpt = torch.load(weights_path, map_location=device)
	model.load_state_dict(ckpt['model'])
	model.classes = ckpt['classes']
	model.resume_epoch = ckpt['epoch']
	if need_ckpt:
		return model, ckpt
	else:
		return model


def load_resume2(weights_path, model, optimizer, device=None):
	print(f"Resume from {weights_path}, ", end='')
	device = device if device is not None else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
	model, ckpt = load_weights(weights_path, model, device=device, need_ckpt=True)
	optimizer.load_state_dict(ckpt['optimizer'])
	# lr_scheduler = ckpt['lr_scheduler']
	print(f'model_dict loaded, optimizer_dict loaded, resume_epoch: {model.resume_epoch}')
	return model, optimizer, model.resume_epoch


def load_resume(weights, model, optimizer, device):
	if weights.endswith('.pt'):  # pytorch format
		ckpt = torch.load(weights, map_location=device)  # load checkpoint
		# load model
		try:
			exclude = ['anchor']  # exclude keys
			ckpt['model'] = {k: v for k, v in ckpt['model'].float().state_dict().items()
							 if k in model.state_dict() and not any(x in k for x in exclude)
							 and model.state_dict()[k].shape == v.shape}
			model.load_state_dict(ckpt['model'], strict=False)
			print('Transferred %g/%g items from %s' % (len(ckpt['model']), len(model.state_dict()), weights))
		except KeyError as e:
			s = "%s is not compatible with %s. This may be due to model differences or config may be out of date. " \
				"Please delete or update %s and try again, or use --weights '' to train from scratch." \
				% (weights, weights, weights)
			raise KeyError(s) from e

		# load optimizer
		if ckpt['optimizer'] is not None:
			optimizer.load_state_dict(ckpt['optimizer'])
			best_fitness = ckpt['best_fitness']

		# load results
		if ckpt.get('training_results') is not None:
			with open(results_file, 'w') as file:
				file.write(ckpt['training_results'])  # write results.txt

		# epochs
		start_epoch = ckpt['epoch']

		del ckpt
		return model, optimizer, best_fitness, start_epoch


def xywh2xyxy(x, need_scale=False, im0=None):
	"""
	convert xcycwh to x1y1x2y2 format, if need_scale, from normalized coor. to pixel coor.
	:param x:
	:param need_sacel:
	:param im0:
	:return:
	"""
	y = np.zeros_like(x)
	y[:, 0] = x[:, 0] - x[:, 2] / 2
	y[:, 1] = x[:, 1] - x[:, 3] / 2
	y[:, 2] = x[:, 0] + x[:, 2] / 2
	y[:, 3] = x[:, 1] + x[:, 3] / 2
	if need_scale:
		h, w = im0.shape[:2]
		y[:, 0] = y[:, 0] * w
		y[:, 1] = y[:, 1] * h
		y[:, 2] = y[:, 2] * w
		y[:, 3] = y[:, 3] * h
		y = y.astype(np.int)
	return y


def letterbox(
		img, new_shape=640, color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, roi=None):
	"""
	resize图像，变成32的的倍数补全
	:param img:
	:param new_shape:
	:param color:
	:param auto:
	:param scaleFill:
	:param scaleup:
	:param roi:
	:return:
	"""
	# Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
	shape = img.shape[:2]  # current shape [height, width]  720, 1280

	if isinstance(new_shape, int):
		new_shape = (new_shape, new_shape)

	# Scale ratio (new / old)
	r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
	if not scaleup:  # only scale down, do not scale up (for better test mAP)
		r = min(r, 1.0)

	# Compute padding
	ratio = r, r  # width, height ratios
	new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
	dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
	# print(dw, dh, ratio)
	if auto:  # minimum rectangle
		dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
	elif scaleFill:  # stretch
		dw, dh = 0.0, 0.0
		new_unpad = (new_shape[1], new_shape[0])
		ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

	# print(dw, dh)
	dw /= 2  # divide padding into 2 sides
	dh /= 2
	# print(new_unpad)

	if shape[::-1] != new_unpad:  # resize
		img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

	# roi
	if roi is not None:
		x1, x2 = roi[0] / shape[1] * new_unpad[0], roi[2] / shape[1] * new_unpad[0]  # convert from pixel to percet
		y1, y2 = roi[1] / shape[0] * new_unpad[1], roi[3] / shape[0] * new_unpad[1]
		img = img[int(y1):int(y2), int(x1):int(x2)]
		rest_h = img.shape[0] % 32
		rest_w = img.shape[1] % 32
		dh = 0 if rest_h == 0 else (32-rest_h)/2
		dw = 0 if rest_w == 0 else (32-rest_w)/2
		recover = [new_shape[0], new_unpad[1], int(x1)-dw, int(y1)-dh]
	else:
		recover = None

	top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
	left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
	img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
	return img, ratio, (dw, dh), recover


def imgAdd(small_img, big_image, x, y, alpha=0.5):
	"""
	把小图贴到大图的xy位置，透明度设置为0.5
	"""
	row, col = small_img.shape[:2]
	if small_img.shape[0] > big_image.shape[0] or small_img.shape[1] > big_image.shape[1]:
		raise NameError(f'imgAdd, the size of small img bigger than big img.')
	roi = big_image[x:x + row, y:y + col, :]
	roi = cv2.addWeighted(small_img, alpha, roi, 1 - alpha, 0)
	big_image[x:x + row, y:y + col] = roi
	return big_image


def plot_confusion_matrix(cm, classes=None):
	"""
	动态刷新多行
	:param cm: confusion matrox
	:return: None
	"""
	data = []

	P, R, F1, acc = dm.general.confusion2score(cm)
	element_lenth = max(6, np.max([len(str(int(x))) for x in cm.reshape(-1)]) + 1)
	if classes is not None:
		element_lenth = max(element_lenth, np.max([len(x) for x in classes]))
		zero = f'    |{" ".join([f"{x:^{element_lenth}}" for x in classes])}\n'
		# print(zero)
		data.append(zero)

	first = f'    |{" ".join([f"{x:^{element_lenth}}" for x in range(len(cm))])}| P\n'
	second = f'----|{"":-<{len(cm)*(element_lenth+1)}}|------\n'
	# print(first)
	# print(second)
	data.append(first)
	data.append(second)
	for i, c in enumerate(cm):
		content = f'{i:>3} |{" ".join([f"{x:^{element_lenth}}" for x in c])}| {P[i]*100:<{element_lenth}.2f}\n'
		# print(content)
		data.append(content)
		# print(c, type(c))
	# print(second)
	data.append(second)
	PRF1 = {'P': P, 'R': R, 'F1': F1}
	PRF1 = {'R': R, 'F1': F1}
	for k in PRF1.keys():
		v = PRF1[k]
		content = f'{k:>3} |{" ".join([f"{x*100:>{element_lenth}.2f}" for x in v])}|\n'
		# print(content)
		data.append(content)
	str_acc = f'acc |{acc*100:>{element_lenth}.2f}|\n'
	# print(str_acc)
	data.append(str_acc)
	data = ''.join(data)
	print(data)
	return data