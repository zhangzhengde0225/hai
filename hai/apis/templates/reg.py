import os, sys
from pathlib import Path

from hai import MODULES, SCRIPTS, IOS  # 算法模块的三个大类
from hai import Config as PyConfigLoader  # 用于加载算法模块的配置文件
from hai import AbstractOutput, AbstractModule, AbstractInput  # 抽象类

pydir = Path(os.path.abspath(__file__)).parent  # 获取当前py文件所在目录


@MODULES.register_module(name='seyolov5')  # 使用装饰器注册模块，将名称为seyolov5的模块注册到MODULES中
class SEYOLOv5(AbstractModule):  # 继承AbstractModule，实现算法模块的基本功能
    name = 'seyolov5'  # 算法模块名称，注意须与注册的名称一致
    status = 'stopped'  # 算法模块的状态，不需修改
    description = '可见光目标检测算法'  # 算法模块的描述信息
    default_cfg = f'{pydir}/config/yolov5_config.py'  # 默认配置文件
    cfg_meta = f'{pydir}/config/config_meta.py'  # 配置文件元信息

    def __init__(self, *args, **kwargs):
        super(SEYOLOv5, self).__init__(*args, **kwargs)  # 初始化父类
        SEYOLOv5.status = 'ready'  # 注册后的模块状态为stopped, 初始化后的状态为ready
        # TODO： 你的模块的初始化代码

    def infer(self, *args, **kwargs):
        SEYOLOv5.status = 'running'
        # xxx 推理代码
        return 'xxx'

    def train(self, *args, **kwargs):
        SEYOLOv5.status = 'running'
        # xxx 训练代码
        return 'xxx'