import os, sys
from pathlib import Path

import hai
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from hai import MODULES, SCRIPTS, IOS, Config

pydir = Path(os.path.abspath(__file__)).parent  # current directory path of this file


@MODULES.register()
class YourModelName(AbstractModule):  # TODO: Change the name of your model
    name = 'YourModelName'  # TODO: Specify the name of your model explicitly
    description = 'Model description'  # TODO: Specify the description of your model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_cfg = 'Your/Default/Model/Configs'  # TODO: Specify the default config of your model
        # The default config can be a dict, json, yaml, a python config file or a config object from argparse
        # and it will be converted to a Config object automatically by the framework
        
    
    def _init_model(self):
        """
        TODO: Please implement your model initialization here
        return: model
        """
        raise NotImplementedError(f'{self.name}._init_model() is not implemented, plese check the api: "{self.__module__}"')

    def train(self, *args, **kwargs):
        """
        TODO: Please implement your model training here
        """
        raise NotImplementedError(f'{self.name}.train() is not implemented, plese check the api: "{self.__module__}"')

    def infer(self, *args, **kwargs):
        """
        TODO: Please implement your model inference here
        """
        raise NotImplementedError(f'{self.name}.infer() is not implemented, plese check the api: "{self.__module__}"')

    def evaluate(self, *args, **kwargs):
        """
        TODO: Please implement your model evaluation here
        """
        raise NotImplementedError(f'{self.name}.evaluate() is not implemented, plese check the api: "{self.__module__}"')