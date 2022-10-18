## 高能物理AI算法框架（HAI）使用教程

HAI平台分为算法框架、模型库、数据集、算力资源四个部分。其中，HAI算法框架集成高能物理领域经典和SOTA的算法，提供统一、简单、易用的接口。

本教程主要介绍如何使用HAI算法框架进行模型训练、模型评估、模型推理和部署。

## Getting Started

检查HAI算法框架是否安装成功：

```bash
hai --version  # Check version
```
如果未安装HAI算法框架，可以`pip install hepai`安装或参考[安装教程](installation.md)。


hai train particle_transformer
### Python接口

```python
import hai

models = hai.hub.list()
print(models)
"""
ID    TYPE    NAME            STATUS   TAG       INCLUDE  DESCRIPTION                                                 
m01   module  YOLOv5          stopped  internal  -        2022 SOTA 目标检测算法YOLOv5-v6                                   
m02   module  ResNet          stopped  internal  -        2015 Classic 残差连接网络ResNet18 34 50 101 152 for classification
IO01  io      ImagesLoader    stopped  -         -        图像数据加载器(支持：image, video, folds, rtsp, rtmp等) hai            
IO02  io      ImagesExporter  stopped  -         -        图像结果输出器   
"""

model_name = 'Particle_Transformer'
# model_name = 'ParticleNet'
# model_name = 'Particle_Flow_Network'
# model_name = 'PCNN'

docs = hai.hub.docs(model_name)  # 文档路径
print('docs:', docs)
model = hai.hub.load(model_name)  # 加载模型对象

print(f'model: {model} {type(model)}')

config = model.config  # 模型的默认配置
config.source = 'TopLandscape'  # 修改配置
# config.source = 'JetClass'
print(config.info())


model.train()  # 启动训练


### 命令行接口(Command Line Interface, CLI)

```bash
hai list  # 列出所有算法、脚本和IO模块
hai MODLE_NAME config  # 查看模型默认配置项
hai load_config CONFIG_PATH  # 加载配置
hai train MODEL_NAME  # 训练模型
hai eval MODEL_NAME  # 评估模型(TODO)
hai infer MODEL_NAME  # 推理模型(TODO)
hai deploy MODEL_NAME  # 部署模型(TODO)，导出onnx/ncnn/tensorrt模型
```



## Contact

如果您对HAI平台有任何需求或建议，欢迎联系我们：zdzhang@ihep.ac.cn
