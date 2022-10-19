
import hai
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from hai import MODULES, SCRIPTS, IOS, Config



@hai.MODULES.register_module(name='YOLOv5')
class YOLOv5v6(AbstractModule):
    name = 'YOLOv5'
    description = '2020 SOTA 目标检测算法YOLOv5-v6'

    def __init__(self, ):
        super().__init__()
        # self._config = _config

    # def get_cfg(self):
        # return self.cfg

    