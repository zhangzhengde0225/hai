"""
保存流的信息
"""
import damei as dm
import numpy as np
from collections import OrderedDict
from .stream import Stream

logger = dm.getLogger('uaii streams')


class Streams(object):

    def __init__(self, cfg, parent):
        self.uaii_cfg = cfg  # 全部的配置
        self._cfg = self.uaii_cfg.streams
        self.parent = parent
        self._name = 'streams'
        self._module_dict = OrderedDict()
        self._init()

    def _init(self):
        cfg = self._cfg
        # print(cfg)
        for i, stream_cfg in enumerate(cfg):
            name = stream_cfg['type']
            # print(stream_cfg)
            stream = Stream(
                parent=self.parent, id=f'S{i + 1:0>2}', stream_cfg=stream_cfg)
            self._module_dict[name] = stream
            # print('xx', stream.seyolov5)

    @property
    def name(self):
        """self name: streams"""
        return self._name

    @property
    def cfg(self):
        """streams cfg"""
        return self._cfg

    @property
    def module_dict(self):
        """OrderedDict, key is the name, value is the stream object"""
        return self._module_dict

    @property
    def ids(self):
        ids = [x[0] for x in self.ps()]
        return ids

    @property
    def names(self):
        """module names"""
        names = [x[2] for x in self.ps()]
        return names

    def verify_input_cfg(self, cfg):
        """校验必要键：type, models"""
        keys = list(cfg.keys())
        if 'type' not in keys:
            raise ValueError(f'Config error. Stream cfg must specify "type", keys: {keys}')
        if 'models' not in keys:
            raise ValueError(f'Config error. Stream cfg must specify "models", keys: {keys}')

    def build_new_stream(self, cfgs, **kwargs):
        """
        build new stream by stream cfgs
        :param cfgs: list of module cfgs
            for example:
                [stream1, stream2, stream3], where streamx is a dict
        """
        # print(cfgs, type(cfgs))
        if isinstance(cfgs, dict):
            cfgs = [cfgs]

        # 获取最大的id
        ids = self.ids
        max_id = np.max([int(x[1::]) for x in self.ids]) if len(ids) != 0 else 0  # [s01, s02, s03, ...]
        # print(len(cfgs))
        # is_mono = len(cfgs) == 1
        for i, stream_cfg in enumerate(cfgs):  # 这里是单个或多个流
            # 校验stream_cfg的必须字段是否存在
            self.verify_input_cfg(stream_cfg)

            name = stream_cfg['type']
            is_mono = len(stream_cfg['models']) == 1
            stream = Stream(
                parent=self.parent,
                id=f'S{max_id + i + 1:0>2}',
                stream_cfg=stream_cfg,  # 这里是每个流有单个或多个模型
                is_mono=is_mono, )
            self._module_dict[name] = stream

        # 合并cfg，列表
        self._cfg += cfgs

    def get(self, module_name):
        return self._module_dict[module_name]

    def ps(self, module=None, **kwargs):
        """'ID', 'TYPE', 'NAME', 'STATUS', 'TAG', 'INCLUDE''DESCRIPTION'"""
        include_dict = kwargs.get('include_dict', None)
        modules = module if module else list(self.module_dict.keys())
        if isinstance(modules, str):
            modules = [modules]

        ret = []
        for module_names in modules:
            module = self.get(module_names)
            id = module.id
            type = 'stream'
            name = module.name
            status = module.status
            description = module.description

            include = module.include(format=list)
            if include_dict:  # 字典：模块名转为id
                include = [include_dict[x] for x in include]
                include = f"[{']['.join(include)}]"
                # print(include_dict, include)
            else:
                include = ' '.join(include)
            # config = module.cfg
            # ret.append([id, type, name, status, include, description, config])
            ret.append([id, type, name, status, '-', include, description])
        return ret
