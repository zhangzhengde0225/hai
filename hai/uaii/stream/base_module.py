"""
为各个模块提供抽象类别
"""
from damei.nn.api.utils import Config


class AbstractModule(object):
    name = 'default_name'
    status = 'stopped'
    description = 'default_description'
    default_cfg = None
    cfg_meta = None
    tag = 'cloud'  # default tag, edge or cloud, edge for edge node, cloud for center node

    def __init__(self, default_cfg=None, cfg=None, **kwargs):
        """
        初始化模块，合并配置文件
        """
        AbstractModule.status = 'ready'
        self.name = AbstractModule.name
        self.status = AbstractModule.status
        self.description = AbstractModule.description
        self._cfg = self._init_cfg(default_cfg, cfg, **kwargs)
        self.mi = None
        self.mo = None

    def _init_cfg(self, default_cfg, cfg, **kwargs):
        """
        合并配置文件
        """
        if default_cfg is not None:
            default_cfg = Config.fromfile(default_cfg) if isinstance(default_cfg, str) else default_cfg

        if cfg is not None:
            cfg = Config.fromfile(cfg) if isinstance(cfg, str) else cfg

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
    def cfg(self):
        return self._cfg

    def train(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.train()')

    def infer(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.infer()')

    def evaluate(self, *args, **kwargs):
        raise NotImplementedError(f'{self.name}.evaluate()')

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
