"""
用于场景的
"""
import os
import cv2
from PIL import Image
import numpy as np


def load_vis_lidar_img_only(vis_sp, lidar_sp, stem, model_size=256, suffix='png'):
	vis_p = f'{vis_sp}/{stem}.{suffix}'
	lidar_p = f'{lidar_sp}/{stem}.{suffix}'
	if not os.path.exists(vis_p):
		raise NameError(f'{vis_p} do not exists.')
	if not os.path.exists(lidar_p):
		raise NameError(f'{lidar_p} do not exists.')
	vis = cv2.imread(vis_p)
	lidar = cv2.imread(lidar_p)
	img = imgAdd(lidar, vis, 0, 0, alpha=0.5)
	image = Image.fromarray(img.astype('uint8')).convert('RGB')
	iw, ih = image.size
	w, h = model_size, model_size
	new_image = Image.new('RGB', (w, h),
						  (100, 100, 100))
	nw = w
	nh = int(w * ih / iw)
	image = image.resize((nw, nh), Image.BICUBIC)
	new_image.paste(image, (0, int((h - nh) / 2)))
	image = new_image
	image = np.array(image)

	return image


def imgAdd(small_img, big_image, x, y, alpha=0.5):
	"""
	把小图贴到大图的xy位置，透明度设置为0.5
	"""
	row, col = small_img.shape[:2]
	if small_img.shape[0] > big_image.shape[0] or small_img.shape[1] > big_image.shape[1]:
		raise NameError(f'imgAdd, the size of small img bigger than big img.')
	black = np.array([0, 0, 0])
	mask = cv2.inRange(small_img, black, black)
	roi = big_image[x:x + row, y:y + col, :]

	roi_a = cv2.addWeighted(small_img, alpha, roi, 1 - alpha, 0)
	roi_a = cv2.bitwise_and(roi_a, roi_a, mask=cv2.bitwise_not(mask))
	roi_b = cv2.bitwise_and(roi, roi, mask=mask)
	roi = cv2.add(roi_a, roi_b)

	# roi = cv2.addWeighted(small_img, alpha, roi, 1 - alpha, 0)
	big_image[x:x + row, y:y + col] = roi
	return big_image