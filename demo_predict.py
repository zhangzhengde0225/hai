
import hai

model = hai.hub.load('UNet', weights=f'hai/unet/unet_v1.0.pth')

cfg = model.config
cfg.source = '/home/zzd/datasets/hai_datasets/carvana/imgs'
# cfg.output = '/home/zzd/datasets/hai_datasets/carvana'  # 
# cfg.weights = 'runs/unet_exp/weights/checkpoint_epoch5.pth'
cfg.viz = True
cfg.no_save = False
print(cfg.info())
# exit()

weights = hai.hub.list_weights()
print(weights)

# model.predict()





