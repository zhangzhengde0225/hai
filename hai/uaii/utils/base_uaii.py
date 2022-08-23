"""
提供基本的UAII类，把各种函数封装在这里。
"""
import collections
import os, sys
import numpy as np
import damei as dm
import cv2
import json

logger = dm.getLogger('base_uaii')
from . import general


class BaseUAII(object):
    def __init__(self, **kwargs):
        self._modules = None
        self._scripts = None
        self._ios = None
        self._streams = None
        self._name2cls = None
        self.cfg = None
        self.is_center = kwargs.get('is_center', True)

    def _configure(self):
        """区分云边端模型"""

        is_center = self.is_center
        if is_center:
            return
        # 如果是边缘端，只保留tag为edge的模型
        ms = self.modules  # Registry对象

        valid_ikv = [[i, k, v] for i, (k, v) in enumerate(ms._module_dict.items()) if v.tag == 'edge']

        new_module_dict = collections.OrderedDict()
        new_module_ids = list()
        for i, k, v in valid_ikv:
            new_module_dict[k] = v
            new_module_ids.append(ms._module_ids[i])

        ms._module_dict = new_module_dict
        ms._module_ids = new_module_ids
        # print(ms._module_dict, len(ms._module_dict))
        # print(ms._module_ids)
        # exit()
        # pass

    def register_name2cls(self):
        name2cls = dict()
        for k, v in self.modules.module_dict.items():
            name = k
            name2cls[name] = 'MODULE'
        for k, v in self.scripts.module_dict.items():
            name2cls[k] = 'SCRIPT'
        for k, v in self.streams.module_dict.items():
            name2cls[k] = 'STREAM'
        for k, v in self.ios.module_dict.items():
            name2cls[k] = 'IO'
        return name2cls

    @property
    def modules(self):
        return self._modules

    @property
    def scripts(self):
        return self._scripts

    @property
    def streams(self):
        return self._streams

    @property
    def ios(self):
        return self._ios

    def get_module(self, name, cls=None, *args, **kwargs):
        """根据模块名和类别获取模块，是未初始化的"""
        # print(args, kwargs, cls)
        ps = self.ps(**kwargs)
        # 输入的名字也可以是ID
        exist_names = [x.split()[2] for x in ps.split('\n')[1::]]
        if name not in exist_names:
            exist_ids = [x.split()[0] for x in ps.split('\n')[1::]]
            assert len(exist_ids) == len(exist_names)
            if name in exist_ids:
                name = exist_names[exist_ids.index(name)]
            else:
                raise ModuleNotFoundError(f"Expected module name: '{name}' not found in exist modules: {exist_names}.")

        try:
            cls = cls if cls else self._name2cls[name]
        except Exception as e:
            raise ModuleNotFoundError(
                f'Error: {e}. \nAll modules: {self.modules}.')

        # print(cls)
        if cls == 'MODULE':
            return self.modules.get(name)
        elif cls == 'SCRIPT':
            return self.scripts.get(name)
        elif cls == 'STREAM':
            return self.streams.get(name)
        elif cls == 'IO':
            return self.ios.get(name)
        else:
            raise NotImplementedError(f'UAII get module name: {name} cls: {cls} not implemented.')

    def build_stream(self, cfg, **kwargs):
        """
        根据流配置文件创建新的流，注册到streams里
        cfg: stream config, or module_name
            for example:
            >>> cfg = dict(
            >>>    type='radar_detection_stream',
            >>>    description='雷达目标探测流',
            >>>    models=[
            >>>        dict(type='radardet', cfg=None)
            >>>    ])
            for example2:
            >>> cfg = 'radardet'
        return: stream object
        """
        is_req = kwargs.get('is_req', False)  # 是否gRPC的请求，如果是，返回值需要重新定义，不能返回对象
        name = f'{cfg}_stream' if isinstance(cfg, str) else cfg['type']
        # 判断算法流是否已经存在
        if name in self.streams.names:
            logger.warn(f'Build stream, name:{name} exist, return existing stream.')
            if is_req:
                return 0, f'stream: {name} exist.'  # 失败0，成功1
            else:
                return self.get_stream(name=name)

        # 创建新的算法流
        if isinstance(cfg, str):  # 就自动配置一个单模块流
            m_name = cfg
            module_desc = self.get_module(m_name).description
            cfg = dict(
                type=f'{m_name}_stream',
                description=f'mono {module_desc} stream',
                models=[
                    dict(
                        type=m_name,
                    )
                ]
            )
        # print(cfg)
        self.streams.build_new_stream(cfg, **kwargs)

        if is_req:
            return 1, name
        else:
            return self.get_stream(name)

    def get_stream(self, name):
        """获得存在的流，并初始化内部的所有模块"""
        stream = self.get_module(name=name, cls='STREAM')
        return stream

    def get_stream_info(self, stream=None, stream_name=None, **kwargs):
        """获得流的信息"""
        is_req = kwargs.pop('is_req', False)
        stream = stream if stream else stream_name
        stream = self.get_stream(stream) if isinstance(stream, str) else stream
        assert stream is not None, f'Stream: {stream} not found.'
        if is_req:
            return 1, stream.info(**kwargs)
        return stream.info(**kwargs)

    def get_stream_cfg_meta(self, stream=None, stream_name=None, addr='/', **kwargs):
        """获得流的配置文件的元信息"""
        is_req = kwargs.pop('is_req', False)
        ret_fmt = kwargs.pop('ret_fmt', 'Config object')

        stream = stream if stream else stream_name
        stream = self.get_stream(stream) if isinstance(stream, str) else stream
        assert stream is not None, f'Stream: {stream} not found.'
        config_meta = stream.get_cfg_meta(addr=addr, **kwargs)
        if is_req:
            return 1, config_meta.to_json()
        else:
            if ret_fmt == 'Config object':
                return config_meta
            elif ret_fmt == 'dict':
                return config_meta.to_dict()
            elif ret_fmt == 'json':
                return config_meta.to_json()
            else:
                raise NotImplementedError(f'UAII get_stream_cfg_meta ret_fmt: {ret_fmt} not implemented.')

    def get_stream_cfg(self, stream=None, stream_name=None, addr='/', **kwargs):
        """
        获得流的配置参数
        """
        is_req = kwargs.pop('is_req', False)  # 是否gRPC的请求，如果是，返回值需要重新定义，
        ret_fmt = kwargs.pop('ret_fmt', 'Config object')  # 返回格式，默认是xai.Config对象
        assert ret_fmt in ['Config object', 'dict'], f'Ret format: {ret_fmt} not supported.'

        stream = stream if stream else stream_name
        stream = self.get_stream(stream) if isinstance(stream, str) else stream
        assert stream is not None, f'Stream: {stream} not found.'
        config = stream.get_cfg(addr=addr, **kwargs)
        # print(config)
        # logger.info(f'Get stream config: {config} {type(config)}')
        if is_req:
            return 1, config.to_json()
        else:
            if ret_fmt == 'Config object':
                return config
            return config.to_json()

    def get_stream_status(self, stream, **kwargs):
        """获得流的状态"""
        is_req = kwargs.pop('is_req', False)
        stream = self.get_stream(stream) if isinstance(stream, str) else stream
        assert stream is not None, f'Stream: {stream} not found.'
        if is_req:
            return 1, stream.status
        return stream.status

    def set_stream_cfg(self, cfg, stream=None, stream_name=None, addr='/', **kwargs):
        """
        设置流的参数
        :param cfg:  流的参数配置，dict, list, str, int, float, bool, etc.
        :param stream: 流对象，如果为None，则根据stream_name获取流对象, xai.Stream对象
        :param stream_name: 流名称，str
        :param addr: 需要修改的流配置的的地址，str
            for example:
                addr = '/'  # 表示修改整个配置
                addr = '/model_name'  # 表示修改流内某个model配置
                addr = '/model_name/param_name'  # 表示修改流内某个model的具体某个param配置，以此类推
        :return: uaii调用时返回xai.Config对象
                grpc调用时返回(1, 字典类型的配置) or (0, 错误信息)
        """
        is_req = kwargs.pop('is_req', False)  # 是否gRPC的请求，如果是，返回值需要重新定义，不能返回对象
        stream = stream if stream else stream_name
        stream = self.get_stream(stream) if isinstance(stream, str) else stream
        assert stream is not None, f'Stream not found. {stream}'
        config = stream.set_cfg(addr=addr, value=cfg, **kwargs)
        # print(config)
        if is_req:
            return 1, config.to_json()
        else:
            return config

    def get_model(self, name):
        """读取单独的模块，内部是把单独的模块组装成流"""
        exists_streams = self.streams.names
        if name in exists_streams:
            mono_flow = self.get_module(name=name, cls='STREAM')
        else:
            cfg = dict(
                type=f'{name}_flow',
                description=f'mono module flow: {name}',
                models=[
                    dict(type=name, cfg=None),
                ]
            )
            mono_flow = self.build_stream(cfg=cfg)
        return mono_flow

    def stream_info(self, name):
        return self.get_stream(name=name).info()

    def ps(self, stream=None, module=None, io=None, script=None, **kwargs):
        """返回全部模块的状态"""
        ret_fmt = kwargs.get('ret_fmt', 'string')
        xai_type = kwargs.get('type', None)  # xai_type: 'stream', 'module', 'io', 'script'
        if xai_type is None:
            pass
        else:
            if xai_type == 'stream':
                stream = True
            elif xai_type == 'module':
                module = True
            elif xai_type == 'io':
                io = True
            elif xai_type == 'script':
                script = True
            else:
                raise ValueError(f'xai_type: {xai_type} not supported.')

        ps0 = [['ID', 'TYPE', 'NAME', 'STATUS', 'TAG', 'INCLUDE', 'DESCRIPTION']]
        if stream is None and module is None and io is None and script is None:
            tmp = self.streams.ps(include_dict=self.modules.name2id_dict)
            ps0 += tmp
            tmp2 = self.modules.ps(include_dict=self.ios.name2id_dict)
            ps0 += tmp2
            ps0 += self.ios.ps()
            # print(ps0, len(ps0))
            # ps0.append(self.scripts.ps())
        else:
            if stream:
                tmp = self.streams.ps(include_dict=self.modules.name2id_dict)
                ps0 += tmp
            if module:
                tmp = self.modules.ps(include_dict=self.modules.name2id_dict)
                ps0 += tmp
            if io:
                ps0 += self.ios.ps(module=None)
            if script:
                ps0 += self.scripts.ps(module=None)
        # ps_all = ps0
        # lenth = np.array([[len(x) for x in xx] for xx in ps_all])  # (n, 4)
        # print()
        # lenth = np.max(lenth, axis=0)  # (4,)
        # ps_list = [[f'{x:<{lenth[i]}}' for i, x in enumerate(xx)] for xx in ps_all]
        # ps_str = '\n'.join(['  '.join(x) for x in ps_list])
        if ret_fmt == 'string':
            return dm.misc.list2table(ps0)
        elif ret_fmt == 'json':
            return json.dumps(ps0, indent=4, ensure_ascii=False)
        elif ret_fmt == 'list':
            return ps0
        else:
            raise NotImplementedError(f'{ret_fmt} not implemented.')

    def show_vis(self, ret, im0, target_names):

        return general.single_plot(ret, im0, target_names=target_names)
