"""
为各个模块提供抽象类别
"""
import argparse
from curses import noecho
import os
from tkinter import N
# from damei.nn.api.utils import Config
from ..utils.config_loader import PyConfigLoader as Config


class AbstractModule(object):
    name = 'default_name'
    status = 'stopped'
    description = 'default_description'
    # default_cfg = None
    cfg_meta = None
    tag = 'cloud'  # default tag, edge or cloud, edge for edge node, cloud for center node

    def __init__(self,cfg=None, **kwargs):
        """
        初始化模块，合并配置文件
        """
        AbstractModule.status = 'ready'
        self._name = AbstractModule.name
        self.status = AbstractModule.status
        self.description = AbstractModule.description
        # self.default_cfg = AbstractModule.default_cfg
        self.default_cfg = None
        # print(default_cfg)
        # self._cfg = self._init_cfg(self.default_cfg, cfg, **kwargs)
        self._cfg = None
        self._model = None
        self.mi = None
        self.mo = None
        # print(f'xxx {self.name}:? {self.status}')
    
    def convert_config_type(self, cfg):
        """
        conver the config type from Config object, .py file argparse.Namespace to Config object
        """
        if isinstance(cfg, Config):
            return cfg
        elif isinstance(cfg, str):
            return Config.fromfile(cfg)
        elif isinstance(cfg, dict):
            return Config.from_dict(cfg)
        elif isinstance(cfg, argparse.Namespace):
            return Config.from_argparse(cfg)
        else:
            raise TypeError(f'{self.name}: {cfg} is not a valid config: {type(cfg)}')
        

    def _init_cfg(self, default_cfg, cfg, **kwargs):
        """
        init config
        :param default_cfg: .py file or Config object or ArgumentParser object 
        :param cfg: .py file or Config object or 
        """
        if default_cfg is not None:
            default_cfg = self.convert_config_type(default_cfg)
                
        if cfg is not None:
            cfg = self.convert_config_type(cfg)
            # cfg = Config.fromfile(cfg) if isinstance(cfg, str) else cfg

        if default_cfg and cfg:
            cfg = default_cfg.merge(cfg2=cfg)
        elif default_cfg:
            cfg = default_cfg
        elif cfg:
            cfg = cfg
        else:
            cfg = None
        return cfg
    
    @property
    def name(self):
        if self._name == 'default_name':
            return self.__class__.__name__
        return self._name

    @property
    def cfg(self):
        # print(self.default_cfg)
        if self._cfg is None:
            self._cfg = self._init_cfg(default_cfg=self.default_cfg, cfg=None)
        return self._cfg

    @property
    def config(self):
        """alias of cfg"""
        return self.cfg

    # @property
    # def model(self):
    #     if self._model is None:
    #         self.build_model()
    #     return self._model

    def build_model(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.build_model() not implemented, plese check the api: "{self.__module__}"')
   
    def get_config(self):
        """alias of cfg"""
        return self.cfg

    def get_cfg(self):
        return self.cfg

    def forward(self, x, *args, **kwargs):
        return self.model(x)

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def train(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.train() not implemented, plese check the api: "{self.__module__}"')

    def infer(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.infer() not implemented, plese check the api: "{self.__module__}"')

    def predict(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.predict() not implemented, plese check the api: "{self.__module__}"')

    def evaluate(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.evaluate() not implemented, plese check the api: "{self.__module__}"')

    def before_train_run(self, *args, **kwargs):
        pass

    def before_train_epoch(self, *args, **kwargs):
        pass

    def before_train_iter(self, *args, **kwargs):
        pass

    def after_train_iter(self, *args, **kwargs):
        pass

    def after_epoch(self, *args, **kwargs):
        pass

    def after_run(self, *args, **kwargs):
        pass
