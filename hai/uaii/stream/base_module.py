"""
为各个模块提供抽象类别
"""

import hai
import argparse
import os
import damei as dm
# from damei.nn.api.utils import Config
from ..utils.config_loader import PyConfigLoader as Config


class AbstractModule(object):
    name = 'default_name'
    status = 'stopped'
    description = 'default_description'
    # default_cfg = None
    cfg_meta = None
    tag = 'internal'

    def __init__(self,cfg=None, **kwargs):
        """
        初始化模块，合并配置文件
        """
        AbstractModule.status = 'ready'
        self._name = AbstractModule.name
        self.status = AbstractModule.status
        self.description = AbstractModule.description
        self.default_cfg = None
        self._mapping = None
        
        self._cfgs = None  # all configs
        self._train_cfg = None
        self._infer_cfg = None
        self._eval_cfg = None

        self._model = None
        self._device = None
        self._mode = 'train'  # mode: train, eval, infer
        
        
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
            return Config.from_argparse(cfg, name=f'{self.name}_config')
        elif isinstance(cfg, dm.misc.fake_argparse.FakeArgparse):
            return Config.from_dm_argparse(cfg, name=f'{self.name}_config')
        else:
            raise TypeError(f'{self.name}: {cfg} is not a valid config type: {type(cfg)}')
        

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
        else:  # empty config
            cfg = Config()
            # print(f'{self.name}: empty config, cfg: {cfg}')
        return cfg

    @property
    def name(self):
        if self._name == 'default_name':
            return self.__class__.__name__
        return self._name
    
    @property
    def mode(self):
        return self._mode

    @property
    def train_cfg(self):
        if self._train_cfg is None:
            raise AttributeError(f'{self.name}: train_cfg is None, please set self._train_cfg in __init__()')
        elif not isinstance(self._train_cfg, hai.Config):
            self._train_cfg = hai.Config.from_anything(self._train_cfg)
            # raise TypeError(f'{self.name}: train_cfg must be a Config object, but got {type(self._train_cfg)}')
        return self._train_cfg
    
    @property
    def eval_cfg(self):
        return self._eval_cfg
    
    @property
    def infer_cfg(self):
        return self._infer_cfg

    @property
    def cfg(self):
        """return the config of the model in current mode"""
        if self.mode == 'train':
            return self.train_cfg
        elif self.mode == 'eval':
            return self.eval_cfg
        elif self.mode == 'infer':
            return self.infer_cfg
        else:
            raise ValueError(f'{self.name}: mode "{self.mode}" is not supported')

    @property
    def cfgs(self):
        return self._cfgs

    @property
    def config(self):
        """alias of cfg"""
        return self.cfg

    @property
    def mapping(self):
        return self._mapping

    @property
    def mapped_config(self):
        if self.mapping is None:
            return self.cfg
        else:
            assert isinstance(self.mapping, dict), f'{self.name}: mapping must be a dict'
            return self.config.map_keys(self.mapping, new=True)

    @property
    def device(self):
        if self._device is None:
            import torch
            device = self.cfg.device
            if device == 'cpu':
                pass
            else:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self._device = device
        return self._device


    @property
    def model(self):
        if self._model is None:
            try:
                model = self.build_model()
            except:
                model = self._init_model()
            if model is not None:  # build_model有可能是返回构建的模型，也有可能是直接在函数中辅助self._model
                self._model = model
        return self._model

    def _init_model(self, *args, **kwargs):
        """init model"""
        raise NotImplementedError(f'{self.name}._init_model() not implemented, plese check the api: "{self.__module__}"')

    def build_model(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.build_model() not implemented, plese check the api: "{self.__module__}"')
   
    def get_config(self):
        """alias of cfg"""
        return self.cfg

    def set_config(self, cfg=None, *args, **kwargs):
        """设置配置"""
        # old_cfg = self.cfg
        self.config.merge(cfg2=cfg, **kwargs)
        
        for key, value in kwargs.items():
            if key == 'weights' and value.startswith('hai/'):  # 替换成hai路径，TODO：支持下载模型权重并替换
                value = value.replace('hai/', f'{hai.config.WEIGHTS_ROOT}/')
            self.config[key] = value

    def get_cfg(self):
        return self.cfg

    def switch(self, mode):
        self._mode = mode

    def switch_train(self):
        self.switch('train')

    def switch_eval(self):
        self.switch('eval')

    def switch_infer(self):
        self.switch('infer')

    def switch_evalute(self):
        """alias of switch_eval"""
        self.switch_eval()

    def switch_inference(self):
        """alias of switch_infer"""
        self.switch_infer()

    def __call__(self, x, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.__call__() not implemented, plese check the api: "{self.__module__}"')

    def forward(self, x):
        return self.model(x)

    def train(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.train() not implemented, plese check the api: "{self.__module__}"')

    def infer(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.infer() not implemented, plese check the api: "{self.__module__}"')

    def predict(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.predict() not implemented, plese check the api: "{self.__module__}"')

    def evaluate(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.evaluate() not implemented, plese check the api: "{self.__module__}"')

    def eval(self, *args, **kwargs):
        return self.evaluate(*args, **kwargs)
        
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

    

