import hai
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from hai import MODULES, SCRIPTS, IOS, Config


@hai.MODULES.register_module(name='ResNet')
class ResNet(AbstractModule):
    name = 'ResNet'
    description = '残差连接网络ResNet18 34 50 101 152'

    def __init__(self, config):
        super().__init__(config)
        self.config = config