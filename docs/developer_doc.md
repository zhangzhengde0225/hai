
作为本项目算法算法模块的开发者，请查看本文档。

本文档的意图：使用本文档，可以明白算法模块与XAI算法平台的关系，掌握如何将已开发好的算法模块集成到XAI算法平台中。

## 算法平台与算法模块的关系
+ XAI算法平台是统一管理算法模块的工具，算法模块是算法平台的一个组件。
+ 算法模块提供算法的包含但不限于模型加载、推理、训练、测试等功能
  1. 算法模块可分类三类：模块、脚本和IO
  2. 其中，模块可以是人工智能算法、机器学习算法、雷达算法等
  3. 脚本提供某些功能，如数据集格式转换、离线处理方法等
  4. IO提供数据的输入和输出功能
+ 算法平台对外提供统一的接口，包括组件自定义、算法配置、性能评估、模块连接关系、算法结果推流等。
  1. 接口分为：python SDK和gRPC接口

## 注册模块
+ 算法模块到XAI算法平台的集成是通过注册模块的方式实现的。
+ 开发者完成一个算法模块的开发后，把源码复制到特定的位置，使用装饰器`@MODULES.register_module(name='/your/module_name')`进行注册
+ XAI启动过程中，会自动检测到注册的模块，并将其加载到算法平台中

#### XAI启动并发现算法模块的过程(以seyolov5为例)：
+ XAI启动，依次调用：
  1. `xsensing_ai/__init__.py`中的`from xsensing_ai.modules import *`
  2. `xsensing_ai/modules/__init__.py`中的`from .detection import *`
  3. `xsensing_ai/modules/detection/__init__.py`中的`from .seyolov5 import *`
+ 在`xsensing_ai/modules/detection/seyolov5/__init__.py`中发现装饰器`@MODULES.register_module(name='seyolov5')`，
并将其解析为算法模块并注册到MODULES中。其他模块、脚本和IO的注册方式同理。

因此，将源码拷贝后，需要在各级`__init__.py`中添加`from xx import *`代码。

#### 注册示例：
以irdet为例，算法属于检测算法的一种，初始的源码应放在`xsensing_ai/modules/detection/irdet/irdet`中，
注意此处有两级`irdet/irdet`。

结构如下：
```
xsensing_ai/modules/detection/irdet/
  ├── irdet (开发完的算法模块源代码)
  ├── config (算法模块的配置文件和配置文件的元数据)
    ├── yolov5_config.py (算法模块的配置文件)
    └── config_meta.py (算法模块的配置文件元数据)
  └── __init__.py (模块的初始化文件，用于算法模块注册)
```
下面介绍__init__.py和config配置文件的编写规则：

## `__init__.py`
`__init__.py`是算法模块的初始化文件，用于算法模块到XAI平台的注册。

以seyolov5为例，内容如下：
```python
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent  # 获取当前__init__.py文件所在目录

from xsensing_ai import MODULES, SCRIPTS, IOS  # 算法模块的三个大类
from xsensing_ai import Config as PyConfigLoader  # 用于加载算法模块的配置文件
from xsensing_ai import AbstractOutput, AbstractModule, AbstractInput  # 抽象类


@MODULES.register_module(name='seyolov5')  # 使用装饰器注册模块，将名称为seyolov5的模块注册到MODULES中
class SEYOLOv5(AbstractModule):   # 继承AbstractModule，实现算法模块的基本功能
    name = 'seyolov5'  # 算法模块名称，注意须与注册的名称一致
    status = 'stopped'  # 算法模块的状态，不需修改
    description = '可见光目标检测算法'  # 算法模块的描述信息
    default_cfg = f'{pydir}/config/yolov5_config.py'  # 默认配置文件
    cfg_meta = f'{pydir}/config/config_meta.py'  # 配置文件元信息
        
    def __init__(self, *args, **kwargs): 
        super(SEYOLOv5, self).__init__(*args, **kwargs)  # 初始化父类
        SEYOLOv5.status = 'ready'   # 注册后的模块状态为stopped, 初始化后的状态为ready
        # TODO： 你的模块的初始化代码
        
    def infer(self, *args, **kwargs):
        SEYOLOv5.status = 'running'
        # xxx 推理代码
        return xxx
    
    def train(self, *args, **kwargs):
        SEYOLOv5.status = 'running'
        # xxx 训练代码
        return xxx
```
#### 说明：
+ 装饰器```@MODULES.register_module(name='seyolov5')```将模块SEYOLOv5注册到注册表registry中。
  参数name是注册的模块名，如果为None默认使用类名作为模块名。
  提供了两个注册表：MODULES是完整的某个功能的实现，SCRIPTS是一些小功能的脚本。
    
+ 类内的name是类内部的名字。
  
+ status是类模块的状态。
  
    - stopped: 注册了但未初始化的模块，可以进行模块连接等操作。
    - ready:   初始化了但未运行的模块。
    - running: 正在运行的模块，不区分训练、推理或测试等。
      
+ description是类模块的描述信息。

### 配置文件
关于配置文件的写法。
每个算法模块需要有一个配置文件，存储默认的配置，以支持平台动态配置。

写成python的字典的格式，即键值对形式，主要的三个键：model，input，output。
+ model: 存储模型配置信息
+ input: 存储输入配置信息
+ output: 存储输出配置信息

例如：
seyolov5模块的配置文件保存在 ：xsensing_ai/modules/detection/seyolov5/config/seyolov5_config.py

内容如下：
```python
model = dict(
  type='seyolov5',
  device='0',
  weights='~/weights/xsesning/yolov5x_3.0.pt',
)
input = dict(
  type='vis_loader',
  source='~/data/vis',
  img_size=640,
)
output = dict(
  ...
)
```

## 配置文件元数据
关于配置文件元数据的写法。
每个算法模块可以指定配置文件元数据，用于存储配置文件的每一项的默认值、描述、类型、是否固定、取值范围等信息，以便于平台查看。

例如：seyolov5的配置文件元数据保存在
xsensing_ai/modules/detection/seyolov5/config/cfg_meta.py

内容如下：
```python
model = dict(  # 关于模型的描述
    desc='关于模型的各项配置',
    type=dict(
        default='seyolov5',  # 参数的默认值
        desc='模型的名字',  # 参数的描述
        dtype='字符串',  # 参数的数据类型
        is_fixed=True,  # 参数是否固定，没有写的就是False
        ),
    device=dict(
        default='0',
        desc='运行设备GPU或CPU, cpu代表使用cpu, 0代表使用第0块GPU，0,1代表同时使用0和1块GPU',
        dtype='字符串',
        range='计算节点拥有的计算设备',  # 参数的取值范围
        ),
    ...
)
input = dict(
  ...
)
```
