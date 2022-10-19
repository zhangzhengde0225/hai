
import hai

models = hai.hub.list()
print(models)
# exit()

# model_name = 'UNet'
model_name = 'Particle_Transformer'
model_name = 'ParticleNet'
model_name = 'Particle_Flow_Network'
model_name = 'PCNN'

docs = hai.hub.docs(model_name)
print('docs:', docs)
model = hai.hub.load(model_name)

print(f'model: {model} {type(model)}')
# config = model.config()

config = model.config  # Default config of model, a hai.Config object
# config.source = '/home/zzd/datasets/hai_datasets/carvana'
config.source = 'TopLandscape'
config.source = 'JetClass'
print(config.info())


model.train()

# uaii = hai.UAII(is_center=True)
# print(uaii.ps())  # 接口所有信息
# print(uaii.get_module('IO01'))

# model = hai.hub.load('')
# model = hai.model.load('YOLOv5_v6')

# print(model)


exit()
# print(uaii.stream_info(name='visible_tracking_stream'))  # 打印流的配置信息
result = uaii.run_stream(stream='visible_tracking_stream')
for i, data in enumerate(result):
    print(i, data)  # 连续运行流的输出结果
