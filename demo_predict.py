

from re import T
import hai

model = hai.hub.load('UNet')

cfg = model.config
cfg.source = '/home/zzd/datasets/hai_datasets/carvana/imgs'
# cfg.output = '/home/zzd/datasets/hai_datasets/carvana'  # 
cfg.weights = 'runs/unet_exp/weights/checkpoint_epoch5.pth'
cfg.viz = True
cfg.no_save = False
print(cfg.info())

model.predict()





