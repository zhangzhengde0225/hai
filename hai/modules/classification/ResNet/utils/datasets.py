import os
import torchvision.transforms as transforms
import torch
import torchvision.datasets as datasets
import numpy as np
from pathlib import Path
import random
from PIL import Image
import cv2
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import yaml


class Places365DataLoader(object):
	def __init__(self):
		self.normalize = transforms.Normalize(
			mean=[0.485, 0.456, 0.406],
			std=[0.229, 0.224, 0.225])

	def get_train(self, traindir, batch_size=8):
		workers = np.min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
		train_loader = torch.utils.data.DataLoader(
			datasets.ImageFolder(traindir, transforms.Compose([
				transforms.RandomResizedCrop(224),
				transforms.RandomHorizontalFlip(),
				transforms.ToTensor(),
				self.normalize,
			])),
			batch_size=batch_size, shuffle=True,
			num_workers=workers, pin_memory=True)
		return train_loader

	def get_val(self, valdir, batch_size=8):
		workers = np.min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
		val_loader = torch.utils.data.DataLoader(
			datasets.ImageFolder(valdir, transforms.Compose([
				transforms.Resize(256),
				transforms.CenterCrop(224),
				transforms.ToTensor(),
				self.normalize,
			])),
			batch_size=batch_size, shuffle=False,
			num_workers=workers, pin_memory=True)
		return val_loader


class SboxDataLoader(object):
	def __init__(self):
		a = 0

	def get_train(self, train_path, batch_size=8):
		workers = np.min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
		datasets = SboxDatasets(train_path)
		train_loader = torch.utils.data.DataLoader(
			datasets,
			batch_size=batch_size,
			shuffle=False,
			num_workers=workers,
			pin_memory=True
		)

		return train_loader

	def get_val(self, val_path, batch_size=8):
		workers = np.min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
		datasets = SboxDatasets(val_path)
		val_loader = torch.utils.data.DataLoader(
			datasets,
			batch_size=batch_size,
			shuffle=False,
			num_workers=workers,
			pin_memory=True
		)
		return val_loader


class SboxDatasets(torch.utils.data.dataset.Dataset):
	"""
	注意，这里有数据融合，vis和雷达的数据
	"""
	def __init__(self, path):
		super(SboxDatasets, self).__init__()
		self.path = path
		self.sensors = ['vis', 'velodyne']
		self.suffix = 'png'
		self.scenes = self.get_scenes(path)
		print(f'scenes: {self.scenes}')
		self.data = self.get_all_files()  # 数据集的所有绝对路径，融合过了的。每个file两个路径

	def __len__(self):
		return len(self.data)

	def __getitem__(self, idx):
		data = self.data
		n = len(self.data)
		# img, target = self.get_one_data(data, idx, model_size=224, enhance_size=True)
		img, target = self.get_one_data(data, idx, model_size=256, enhance_size=False)
		img = np.array(img, dtype=np.float32)
		img = np.transpose(img/255.0, (2, 0, 1))
		target = np.array(target, dtype=np.int)
		return img, target

	def get_one_data(self, data, idx, model_size=224, enhance_size=False, hue=.1, sat=1.5, val=1.5):
		paths = data[idx]
		vis = cv2.imread(paths[0])
		lidar = cv2.imread(paths[1])
		img = self.imgAdd(lidar, vis, 0, 0, alpha=0.5)
		# cv2.imwrite('xx.png', img)
		image = Image.fromarray(img.astype('uint8')).convert('RGB')
		iw, ih = image.size
		w, h = model_size, model_size

		if enhance_size:
			# 调整图片大小
			jitter = 0.3
			new_ar = w / h * self.rand(1 - jitter, 1 + jitter) / self.rand(1 - jitter, 1 + jitter)  # w/h * (0.53~1.85)
			scale = self.rand(.25, 2)  # (0~1)*1.75 + 0.25 = (0.25~1.75)
			if new_ar < 1:  # w比h小
				nh = int(scale * h)  # 416*(0.25~1.75)
				nw = int(nh * new_ar)
			else:  # h比w小
				nw = int(scale * w)
				nh = int(nw / new_ar)
			image = image.resize((nw, nh), Image.BICUBIC)

			# 放置图片
			dx = int(self.rand(0, w - nw))
			dy = int(self.rand(0, h - nh))
			new_image = Image.new('RGB', (w, h),
							  	(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
			new_image.paste(image, (dx, dy))
			image = new_image
		else:
			new_image = Image.new('RGB', (w, h),
								  (100, 100, 100))
			nw = w
			nh = int(w*ih/iw)
			image = image.resize((nw, nh), Image.BICUBIC)
			new_image.paste(image, (0, int((h-nh)/2)))
			image = new_image

		# 是否翻转图片
		flip = self.rand() < .5
		if flip:
			image = image.transpose(Image.FLIP_LEFT_RIGHT)

		# 色域变换
		hue = self.rand(-hue, hue)
		sat = self.rand(1, sat) if self.rand() < .5 else 1 / self.rand(1, sat)
		val = self.rand(1, val) if self.rand() < .5 else 1 / self.rand(1, val)
		x = rgb_to_hsv(np.array(image) / 255.)
		x[..., 0] += hue
		x[..., 0][x[..., 0] > 1] -= 1
		x[..., 0][x[..., 0] < 0] += 1
		x[..., 1] *= sat
		x[..., 2] *= val
		x[x > 1] = 1
		x[x < 0] = 0
		image_data = hsv_to_rgb(x) * 255  # numpy array, 0 to 1

		# 处理目标
		target = np.zeros(len(self.scenes)).astype(np.int)
		scene = Path(Path(paths[0]).parent).stem
		idx = self.scenes.index(scene)
		target[idx] = 1
		target = idx  # 为了配合place365的格式，还是写成索引的形式，而不是独热编码
		return image_data, target

	def get_scenes(self, path):
		folds = [x for x in os.listdir(path) if os.path.isdir(f'{path}/{x}')]
		# print(folds)
		return sorted(folds)

	def get_all_files(self):
		files = []
		sensors = self.sensors
		suffix = self.suffix
		for scene in self.scenes:
			stems = [Path(x).stem.split('_')[-1] for x in os.listdir(f'{self.path}/{scene}') if 'vis' in x]
			# print(len(stems), stems)
			for stem in stems:
				paths = [
					f'{self.path}/{scene}/{sensors[0]}_{stem}.{suffix}',
					f'{self.path}/{scene}/{sensors[1]}_{stem}.{suffix}']
				files.append(paths)
		# print(len(files), files[:10])
		random.shuffle(files)
		# print([x for x in files[:10]])
		return files

	def imgAdd(self, small_img, big_image, x, y, alpha=0.5):
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

	def rand(self, a=0, b=1):
		return np.random.rand() * (b - a) + a  # (2*jitter) + (1-jitter)  (0~0.6)*0.7 = (0.7~1.3)


class StatusDataLoader(object):
	def __init__(self, balance=True, dformat='TDSC'):
		self.balance = balance
		self.dforamt = dformat

	def get_loader(self, trte_path, cfg, batch_size=8):
		workers = np.min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
		datasets = StatusDatasets(
			trte_path, cfg, balace=self.balance, dformat=self.dforamt)
		train_loader = torch.utils.data.DataLoader(
			datasets,
			batch_size=batch_size,
			shuffle=True,
			num_workers=workers,
			pin_memory=True
		)

		return train_loader


class StatusDatasets(object):
	"""
	类似于场景识别的写法，数据集是格式是每个状态在一张图上，且分开存储在不同的文件夹中，注意，可能有多个路径，即传入的path可以是str也可能是list
	"""
	def __init__(self, path, cfg, balace=True, dformat='TDSC'):
		self.path = [path] if isinstance(path, str) else path
		print(f'Reading data in {path}.')
		assert type(self.path) == list
		self.cfg = cfg
		self.statuses = cfg['statuses']
		self.feature_size = cfg['feature_size']
		self.suffix = '.jpg'
		self.dformat = dformat
		data_uf, self.data = self.get_all_data(balance=balace, dformat=dformat)  # data_uf: un flattened
		print(f'number of items: {len(self.data)}')

	def __len__(self):
		return len(self.data)

	def __getitem__(self, idx):
		data = self.data
		img_path, status, img, target = self.get_one_data(data, idx, use_hue=True)
		img = np.array(img, dtype=np.float32)
		img = np.transpose(img / 255.0, (2, 0, 1))
		target = np.array(target, dtype=np.int64)
		return img, target, img_path, status

	def get_one_data(self, data, idx, use_hue=True, hue=.1, sat=1.5, val=1.5):
		dformat = self.dformat
		fs = self.feature_size
		img_path = data[idx]
		if dformat == 'places365':
			status = Path(Path(img_path).parent).stem
		elif dformat == 'TDSC':
			status = Path(img_path).stem.split('.')[-1]
		elif dformat == 'behavior':
			status = Path(img_path).stem.split('_')[1]
		else:
			raise NotImplementedError
		img = cv2.imread(img_path)
		# print(img_path, status, img.shape)
		# exit()
		assert img.shape[0] == fs[1]  # h
		assert img.shape[1] == fs[0]  # w
		image = Image.fromarray(img.astype('uint8')).convert('RGB')
		if self.cfg['random_flip']:
			flip = self.rand() < .5
			if flip:
				image = image.transpose(Image.FLIP_LEFT_RIGHT)

		if use_hue:
			# 色域变换
			hue = self.rand(-hue, hue)
			sat = self.rand(1, sat) if self.rand() < .5 else 1 / self.rand(1, sat)
			val = self.rand(1, val) if self.rand() < .5 else 1 / self.rand(1, val)
			x = rgb_to_hsv(np.array(image) / 255.)
			x[..., 0] += hue
			x[..., 0][x[..., 0] > 1] -= 1
			x[..., 0][x[..., 0] < 0] += 1
			x[..., 1] *= sat
			x[..., 2] *= val
			x[x > 1] = 1
			x[x < 0] = 0
			image = hsv_to_rgb(x) * 255  # numpy array, 0 to 1

		target = self.statuses.index(status)  # 不是独热编码
		# print('xx', status, target, self.statuses)
		return img_path, status, image, target

	def get_all_data(self, balance=False, dformat='TDSC'):
		"""
		根据路径和状态，获取样本。
		:param balance: 是否启用样本均衡策略
		:param dformat: way to fill data_list
		:return:
		"""
		statuses = self.statuses
		data_list = [[] for _ in range(len(statuses))]
		for i, p in enumerate(self.path):
			# print(p) /home/zzd/datasets/pose/features/9floor/train
			if dformat == 'place365':
				data_list = self.fill_datalist_in_places365_format(data_list, statuses, p)
			elif dformat == 'TDSC':
				data_list = self.fill_datalist_in_TDSC_format(data_list, statuses, p, fformat='TDSC')
			elif dformat == 'behavior':
				data_list = self.fill_datalist_in_TDSC_format(data_list, statuses, p, fformat='behavior')
			else:
				raise NotImplementedError

		# 警告
		for i, s in enumerate(statuses):
			if len(data_list[i]) == 0:
				print(f'WARNING: zero samples read for class: [{s}].')
		# 打印各状态的样本数目
		print(f'number of items in every class:')
		print(f'{" ".join([f"{x:>10}" for x in statuses])}')
		print(f'{" ".join([f"{len(x):>10}" for x in data_list])} {sum([len(x) for x in data_list]):>10}')

		random.seed(930429)
		if balance:
			# 样本均衡的策略是，都取200的4倍，即800，少于800全能取
			num = 800
			data_list = [random.sample(x, num) if len(x) > num else x for x in data_list]
			print(f'均衡后各类样本的数目：')
			print(f'{" ".join([f"{x:>10}" for x in statuses])}')
			print(f'{" ".join([f"{len(x):>10}" for x in data_list])} {sum([len(x) for x in data_list]):>10}')
			# print(np.mean(num_samples), np.max(num_samples)/np.min(num_samples), np.mean(num_samples)/np.min(num_samples))
		# print([len(x) for x in data_list])

		flatten_datalist = []
		for x in data_list:
			flatten_datalist += x
		random.shuffle(flatten_datalist)
		return data_list, flatten_datalist

	def fill_datalist_in_TDSC_format(self, data_list, statuses, p, fformat='TDSC'):
		"""
		从Target Detection and Status Classfication格式的数据集填充datalist
		:param data_list: len: num_statues, empty
		:param statuses: statuses list
		:param p: abs path contains imgs
		:param fformat: fill format. if TDSC, get cls by split '.', if behavoir, get cls by split '_'
				TDSC: img命令格式为：stem.tid.cls.jpg
				bebavior: img命名格式为: feature_cls_stem_tid.jpg
		:return data_list: num_statuses个元素，每个元素内部是该文件的绝对路径
		"""
		imgs = [f'{p}/{x}' for x in os.listdir(p) if x.endswith(self.suffix)]
		# print(len(imgs))
		flag = 0
		for img in imgs:
			if fformat == 'TDSC':
				cls = Path(img).stem.split('.')[-1]
			elif fformat == 'behavior':
				cls = Path(img).stem.split('_')[1]
			else:
				raise NotImplementedError(f'unsupported fformat: {fformat}')
			if cls not in statuses:
				print(f'WARNING: 数据集{p}中读取到了状态{cls}但不存在于配置文件中，忽略。') if flag == 0 else None
				flag = 1
				continue
			cls_idx = statuses.index(cls)
			# print(cls, cls_idx)
			data_list[cls_idx] += [img]
		return data_list

	def fill_datalist_in_places365_format(self, data_list, statuses, p):
		"""
		从places365格式的数据集填充datalist
		该格式为：
		root_path
		|---scene1
		| |--xx.jpg
		| |--...
		|---scene2
		|...
		"""
		for j, s in enumerate(statuses):
			if not os.path.exists(f'{p}/{s}'):
				print(f'WARNING: 路径{p}/{s}不存在')
				continue
			imgs = [f'{p}/{s}/{x}' for x in os.listdir(f'{p}/{s}') if x.endswith(self.suffix)]
			assert len(imgs) > 0
			data_list[j] += imgs
		return data_list

	def get_status_list(self):
		"""
		根据传入的路径，获取路径下的文件夹名作为状态列表
		:return:
		"""
		statuses = []
		for p in self.path:
			statuses += [x for x in os.listdir(p) if x not in statuses]
		print(f'get_status_list: 共计{len(statuses)}个状态：{statuses}')
		return statuses

	def rand(self, a=0., b=1.):
		return np.random.rand() * (b - a) + a  # (2*jitter) + (1-jitter)  (0~0.6)*0.7 = (0.7~1.3)


if __name__ == '__main__':
	"""
	sd_path = "/home/zzd/datasets/fusion/scenes/sc_format/train"
	datasets = SboxDatasets(sd_path)
	for i, data in enumerate(datasets):
		img, target = data
		print(i, img.shape, target, type(img))
		cv2.imwrite(f'tmp/xx_{i}.png', img)
		if i > 20:
			exit()
	"""
	with open('../data/status_pose.yaml', 'r') as f:
		cfg_dict = yaml.load(f, Loader=yaml.FullLoader)
	root_path = cfg_dict['dataset_root_path']
	statuses = cfg_dict['statuses']

	data_paths = [f'{root_path}/{x}/train' for x in os.listdir(root_path)]

	datasets = StatusDatasets(data_paths, statuses)

	for i, data in enumerate(datasets):
		img, target, img_path, status = data
		print(i, img.shape, target, img_path, status)
		exit()



