
import hai
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from hai import MODULES, SCRIPTS, IOS, Config



@hai.MODULES.register_module(name='YOLOv5_v6')
class YOLOv5v6(AbstractModule):
    name = 'YOLOv5_v6'
    description = '目标检测算法'

    def __init__(self, config):
        super().__init__(config)
        self.config = config

