"""
DmControl
control colors for plots
control experiments
"""
# from utils import auto_anchor
import torch
import os
import shutil


class DmControl(object):
	def __init__(self):
		self.dcc = DmColorsControl()

		# self.anch = auto_anchor.AnchorControl()


class DmColorsControl(object):
	def __init__(self):
		self.init_inner_color()

		color_names = ['red', 'gold', 'dodgerblue', 'forestgreen', 'deeppink', 'blueviolet']  # 红 黄 蓝 绿 粉 紫
		self.colors = [self.n(n) for n in color_names]
		deep_color_names = ['darkred', 'goldenrod', 'darkblue', 'darkgreen', 'palevioletred', 'indigo']
		self.deep_colors = [self.n(n) for n in deep_color_names]

	def __call__(self, index, **kwargs):
		"""return color"""
		return self.colors[index]

	def dc(self, index):
		"""return deep color"""
		return self.deep_colors[index]

	def n(self, name):
		"""
		get color from name
		"""
		exec(f'self.tmpc = self.{name}')
		return self.tmpc

	def init_inner_color(self):
		# url: https://www.ip138.com/yanse/selection.htm
		# 红
		self.lightcoral = "#F08080"  # 亮珊瑚色
		self.red = "#EE3B3B"  # 红色
		self.orangered = "#FF4500"  # 红橙色
		self.darkred = "#8B0000"  # 暗红色

		# 金 （黄）
		self.yellow = "FF0000"  # 黄色
		self.gold = "#FFD700"  # 金色
		self.goldenrod = "#DAA520"  # 金麒麟色

		# 蓝
		self.lightskyblue = "#87CEFA"  # 亮天蓝色
		self.dodgerblue = "#1E90FF"  # 闪蓝色
		self.royalblue = "#4169E1"  # 皇家蓝
		self.darkblue = "#00008B"  # 暗蓝色

		# 绿
		self.springgreen = "#00FF7F"  # 春绿色
		self.limegreen = "#32CD32"  # 橙绿色
		self.forestgreen = "#228B22"  # 森林绿
		self.darkgreen = "#006400"  # 暗绿色

		# 粉
		self.pink = "#FFC0CB"  # 粉红色
		self.deeppink = "#FF1493"  # 深粉红色
		self.palevioletred = "#D87093"  # 苍紫罗兰色（比深粉红深）

		# 紫
		self.blueviolet = "#8A2BE2"  # 蓝紫罗兰色
		self.purple = "#800080"  # 紫色
		self.indigo = "#4B0082"  # 靛青色

		# 灰
		self.whitesmoke = "#F5F5F5"  # 烟白色
		self.lightgray = "#D3D3D3"  # 浅灰

		# 黑
		self.black = "#000000"


class DmExperimentControl(object):
	def __init__(self):
		"""
		用于控制训练是实验，实现序号为runs/exp0 exp1 exp2 ...
		function: echo_info: 把传入的info[str], 写入到results.txt
		function: save_mode: 把传入的ckpt写入到传入的model_name中。

		"""
		self.exp = self.get_exp()  # 获取当前实验名称
		self.exp_path = os.path.join(os.getcwd(), f'runs/{self.exp}')
		# self.save_cfg('tiny_config.py')  # 保存config.py
		print(f'current experiment: "{self.exp}", path: {self.exp_path}')

	def get_exp(self):
		if not os.path.exists('runs'):
			os.makedirs('runs')
			os.makedirs('runs/exp0')
			os.makedirs('runs/exp0/weights')
			return 'exp0'
		exist_exp = os.listdir('runs')
		for i in range(100000):
			if i >= 1000:
				raise NameError(f'experiment warning: current experiment index >= 1000, please check.')
			if f'exp{i}' in exist_exp:
				pass
			else:
				os.makedirs(f'runs/exp{i}')
				os.makedirs(f'runs/exp{i}/weights')
				return f'exp{i}'

	def save_cfg(self, cfg):
		# os.system(f'cp {cfg} runs/{self.exp}/config.py')
		shutil.copy(cfg, f'runs/{self.exp}/config.py')

	def echo_info(self, info, txt='results.txt'):
		txt = txt if txt.endswith('.txt') else f'{txt}.txt'
		os.system(f'echo "{info}" >>runs/{self.exp}/{txt}')

	def save_model(self, ckpt, model_name):
		path = f'runs/{self.exp}/weights/{model_name}'
		print(f'Saving model to {path}')
		torch.save(ckpt, path)


if __name__ == '__main__':
	import tiny_net
	import tiny_config
	import tiny_dataset
	cfg = tiny_config.MyConfig()
	dataset = tiny_dataset.MyYoloDataset(cfg.train_txt_path, cfg.model_img_size)
	dataloader = torch.utils.data.DataLoader(
		dataset=dataset,
		batch_size=cfg.batch_size,
		num_workers=8,
		pin_memory=True,
		drop_last=True,
		collate_fn=tiny_dataset.yolo_dataset_collate)
	dm = DmControl()
	dm.anch(dataset)






