"""
基础的流类
"""
import sys

import numpy as np
import collections
import copy
import damei as dm
import json
# from ..utils.config_loader import PyConfigLoader
from damei.nn.api.utils import Config

logger = dm.getLogger('stream')


class Stream(object):
    name = 'stream_name'
    status = 'stopped'
    description = 'stream description'

    def __init__(self, parent, id=None, stream_cfg=None, **kwargs):
        self.is_mono = kwargs.pop('is_mono', False)
        self.name = stream_cfg['type']
        self.status = Stream.status
        self.description = stream_cfg.get('description', Stream.description)
        self.id = id
        self._cfg = stream_cfg
        self.modules_list_config = stream_cfg['models']  # list，每个元素是dict，是模块的配置，type和cfg
        # print('初始化', parent)
        self.parent = parent  # uaii
        self._modules, self._module_cfgs, self._module_cfgs_meta = self.init_about_models()  # 未初始化的模块和对应的配置
        self._inited_modules = collections.OrderedDict()  # 已经初始化的模块
        # self.register_attrs()
        # print('xx', self.seyolov5)

    def __repr__(self):
        format_str = f"<class '{self.__class__.__name__}'> " \
                     f"(name='{self.name}', status='{self.status}', " \
                     f"include={self.include(format=list)}, " \
                     f"description='{self.description}')"
        return format_str

    def init_about_models(self):
        """
        init this stream，read configs, DO NOT init modules.
        :return:
            ordered dict of modules: key is module name, value is module class (not inited)
            ordered dict of module configs: key is module name, value is module config: Config object.
        """
        _modules = collections.OrderedDict()
        _module_cfgs = collections.OrderedDict()
        _module_cfgs_meta = collections.OrderedDict()
        for i, module in enumerate(self.modules_list_config):
            mname = module['type']  # 必须存在
            model_cfg = module.pop('cfg', None)  # 可以为无，默认为None
            module = copy.deepcopy(
                self.parent.get_module(mname, cls='MODULE', module=True))  # copy modeul from registry
            _modules[mname] = module  # 存入模块
            setattr(self, mname, module)  # 存入属性, self.module_name = module
            # cfg = PyConfigLoader(module.default_cfg)  # 这是默认配置
            # assert module.default_cfg is not None, f'"{mname}" has no default_cfg'
            cfg = Config(module.default_cfg)  # 使用模块的默认配置，的

            if model_cfg:  # 如果外部设置流的同时指定了配置文件，合并配置
                full_cfg_path = f'{self.parent.root_path}/{model_cfg}'
                # cfg2 = PyConfigLoader(cfg_file=full_cfg_path, root_path=self.parent.root_path)
                cfg2 = Config(cfg_file=full_cfg_path, root_path=self.parent.root_path)
                cfg = cfg.merge(cfg2)
            _module_cfgs[mname] = cfg

            cfg_meta_file = module.cfg_meta
            cfg_meta = Config(cfg_file=cfg_meta_file)
            _module_cfgs_meta[mname] = cfg_meta

        return _modules, _module_cfgs, _module_cfgs_meta

    def __call__(self, x, *args, **kwargs):
        """模块前馈"""
        # 需要把input封装成mi对象
        self.parent.run_stream(
            self,
            run_in_main_thread=True,
            mtask='infer',
            mi=input,
        )

    def init(self, stream_cfg=None, **kwargs):
        """初始化流内模块
        初始化流的意思的：对流内每个模块进行初始化，并配置好模块的I/O
        模块可能的状态有：stopped, ready, running.
        stopped时，直接初始化
        ready或running时，如果force_init=True, 先停止，再初始化
                如果force_init=False, 则不初始化
        """
        # TODO: 通用的monoflow和multiflow的传入stream_cfg的实现方法
        logger.info(f'Initializing ...')
        force_init = stream_cfg is not None  # 当传入stream_cfg时，强制初始化

        if self.status != 'stopped':
            if force_init:
                self.stop()
            else:
                logger.warning(f'Stream {self.name} is not stopped, skip initialization')
                return

        if self.status == 'stopped':
            models = self.models  # 所有的模型
            model_cfgs = self.model_cfgs  # 所有的配置
            for i, (mname, model) in enumerate(models.items()):
                model_cfg = model_cfgs[mname]
                is_first = i == 0
                is_last = i == len(models) - 1
                # print(model.status, force_init, self.status)
                model = model(cfg=model_cfg)

                mi = self.parent.build_io_instance('input', model_cfg) if is_first else None
                mo = self.parent.build_io_instance('output', model_cfg) if is_last else None

                if mi is not None:
                    if hasattr(model, 'mi'):
                        delattr(model, 'mi')
                    setattr(model, 'mi', mi)
                if mo is not None:
                    if hasattr(model, 'mo'):
                        delattr(model, 'mo')
                    setattr(model, 'mo', mo)

                if hasattr(self, mname):
                    delattr(self, mname)
                setattr(self, mname, model)  # 变成初始化后的模型

                self._inited_modules[mname] = model  # 把初始化后的模型存进去
        else:
            logger.warning(f'Stream {self.name} is not stopped, skip initialization')
        self.status = 'ready'

    def register_attrs(self):
        """把包含的子模块注册为本流的属性"""
        for i, module in enumerate(self.stream_models):
            mname = module['type']
            mtask = module.get('task')
            module = self.parent.get_module(mname, cls='MODULE', module=True)
            setattr(self, mname, module)

    @property
    def cfg(self):
        """流的配置文件，不包含模块的配置"""
        return self._cfg

    @property
    def models(self):
        if self.status == 'stopped':
            return self._modules
        else:
            return self._inited_modules

    @property
    def model_cfgs(self):
        return self._module_cfgs

    @property
    def model_cfgs_meta(self):
        return self._module_cfgs_meta

    @property
    def model_names(self):
        module_names = [x['type'] for x in self.modules_list_config]
        # print(self.models)
        # sys.exit(1)
        return module_names

    def get_config(self, addr='/', **kwargs):
        return self.get_cfg(addr=addr, **kwargs)

    def get_cfg_meta(self, addr='/', **kwargs):
        if self.is_mono:
            addr = f'{addr}/{self.model_names[0]}' if addr == '/' else addr

        if addr == '/':
            stream_cfg = self.cfg
            for mname in self.model_names:
                model_cfg_meta = self.model_cfgs_meta[mname]
                model_cfg_meta_dict = model_cfg_meta.to_dict()
                stream_cfg[mname] = model_cfg_meta_dict
            return Config.from_dict(stream_cfg)
        else:
            attrs = [x for x in addr.split('/') if x != '']
            assert len(attrs) >= 1, 'addr must be like /xxx/xxx/xxx'
            mname = attrs.pop(0)
            cfg_meta = self.model_cfgs_meta[mname]
            for sub_attr in attrs:
                cfg_meta = cfg_meta[sub_attr]
            return cfg_meta

    def get_cfg(self, addr='/', **kwargs):
        """
        获取配置，包含流的配置和子模块的配置，其中mono流的配置即内部模块的配置
        :param addr: 配置路径, 例如：/带代表stream自身配置，/seyolov5代表流的seyolov5模块的配置，/seyolov5/input_stream代表流的模块的input_stream的配置
        :return: 配置dict
        """

        if self.is_mono:
            addr = f'{addr}{self.model_names[0]}' if addr == '/' else addr

        if addr == '/':  # 全部配置
            stream_cfg = self.cfg
            for model_name in self.model_names:
                model_cfg = self.model_cfgs[model_name]
                model_cfg_dict = model_cfg.to_dict()
                stream_cfg[model_name] = model_cfg_dict
            # print(stream_cfg, stream_cfg.keys())
            return Config.from_dict(stream_cfg)
        else:  # 子模块配置
            attrs = [x for x in addr.split('/') if x != '']
            assert len(attrs) >= 1
            mname = attrs.pop(0)  # module name
            cfg = self.model_cfgs[mname]
            for sub_attr in attrs:
                cfg = cfg[sub_attr]
            return cfg

    def set_config(self, value=None, addr='/', **kwargs):
        return self.set_cfg(value, addr, **kwargs)

    def set_cfg(self, value=None, addr='/', **kwargs):
        """
        更新配置
        :param addr: address
        :param value: config value
        :return:
        """
        assert value is not None

        # 处理mono流的配置，当传入的addr是/时，其实是更新里面的模型的配置
        if self.is_mono:  # mono流，传入/时，更新为/model_name
            addr = f'/{self.model_names[0]}' if addr == '/' else addr

        if addr == '/':  # multi-module流, update all
            # 不能修改type, description, models配置项，对每个子模块，都要更新配置
            for model_name in self.model_names:
                model_cfg = self.model_cfgs[model_name]
                new_model_cfg = Config.from_dict(value[model_name])
                model_cfg.merge(new_model_cfg)
            # raise NotImplementedError(f"You cannot set config of the stream")
            return self.get_cfg(addr=addr, **kwargs)
        else:
            attrs = [x for x in addr.split('/') if x != '']
            assert len(attrs) >= 1
            if len(attrs) == 1:  # 即addr=/seyolov5这类情形
                if isinstance(value, dict):
                    value = Config.from_dict(value)
                else:  # 有可能本来就是Config对象，即<class 'damei.nn.uaii.utils.config_loader.PyConfigLoader'>
                    pass
            mname = attrs.pop(0)
            m = self.models[mname]
            if m.status != 'stopped':
                logger.warn(f"Please stop the stream: '{self.name}' while configure it's module.")
                return
            mcfg = self.model_cfgs[mname]
            mcfg.update_item(attrs, value)
            self.model_cfgs[mname] = mcfg
            # print(f'newcfg: {mcfg.info()}')
            return self.get_cfg(addr='/', **kwargs)

    def ps(self, *args, **kwargs):
        return self.info(*args, **kwargs)

    def get_info(self, *args, **kwargs):
        return self.info(*args, **kwargs)

    def info(self, *args, **kwargs):
        ret_fmt = kwargs.get('ret_fmt', 'string')

        info = dict()
        info['class'] = f'<class "{self.__class__.__name__}">'
        info['name'] = self.name
        info['description'] = self.description
        info['status'] = self.status
        info['is_mono'] = self.is_mono

        sub_modules = self.include()
        sub_modules_ids = [self.parent.modules.name2id_dict[x] for x in sub_modules]
        info['models'] = dict(zip(sub_modules_ids, sub_modules))

        models = self.models
        model_cfgs = self.model_cfgs
        for i, (mname, model) in enumerate(models.items()):
            # mname = module['type']
            # mtask = module.get('task', None)
            id = self.parent.modules.name2id_dict[mname]
            cfg = self.model_cfgs[mname]

            # m = self.parent.get_module(name=mname)
            # if m.status == 'stopped':
            #    cfg = PyConfigLoader(m.default_cfg)
            # else:  # ready running
            #    cfg = m.cfg  # 可能会merge之后的也是PyConfigLoader对象

            info[f'{mname} config'] = cfg.items
        # print(ret_fmt)
        # exit()
        if ret_fmt == 'string':
            format_str = self.dict2info(info)
            # format_str += dm.misc.dict2info(info)
            return format_str
        elif ret_fmt == 'dict':
            return info
        elif ret_fmt == 'json':
            return json.dumps(info, indent=4, ensure_ascii=False)
        else:
            raise ValueError(f"Unknown format: {ret_fmt}")

    def dict2info(self, info_dict):
        # 先递归地展开
        new_info_dict = collections.OrderedDict()
        indents = []
        indent_space = 4
        for k, v in info_dict.items():
            self.recursive_func(k, v, new_info_dict, indents, indent_space=indent_space)
        info_dict = new_info_dict

        indents2color = {0: '32m', 1 * indent_space: '35m', 2 * indent_space: '36m', 3 * indent_space: '33m'}
        lenth = np.max([len(x) for x in info_dict.keys()])
        format_str = ''
        for i, (k, v) in enumerate(info_dict.items()):
            indent = indents[i]
            # print(f'k: {k} {len(k)}')
            k_str = f'{k.strip("*"):>{indent + lenth}}'
            color = indents2color.get(indent, None)
            k_str = f'\033[1;{color}{k_str}\033[0m' if color else k_str  # 上色
            format_str += f'  {k_str} : {v}\n'
        return format_str

    def recursive_func(self, k, v, new_info_dict, indents, indent=0, indent_space=4):
        """递归拆分，原来的字典里，某些值可能还是dict，为了方便显示，递归展开，子dict的每个键作为新的顶层的键"""
        if isinstance(v, dict):
            while True:
                if k not in new_info_dict.keys():
                    break
                k = '*' + k
            new_info_dict[f'{k}'] = f'({len(v.keys())})'
            indents.append(indent)
            indent += indent_space
            for k2, v2 in v.items():
                # print(f'k2: {k2} indent: {indent}', new_info_dict.keys())
                self.recursive_func(k2, v2, new_info_dict, indents, indent, indent_space=indent_space)
        else:
            while True:
                if k not in new_info_dict.keys():
                    break
                k = '*' + k
            new_info_dict[f'{k}'] = v
            indents.append(indent)
        return new_info_dict

    def include(self, format=list):
        if format == list:
            return [x['type'] for x in self.modules_list_config]
        else:
            return ' '.join([x['type'] for x in self.modules_list_config])

    def pop(self, wait=True, timeout=None):
        return self.mo.pop(wait=wait, timeout=timeout)

    def get_last(self, wait=True, timeout=None):
        return self.mo.get_last(wait=wait, timeout=timeout)

    def scan(self, last=False):
        return self.mo.scan(last=last)

    def run(self, **kwargs):
        """从stopped运行流"""
        return self.parent.run(self, **kwargs)  # run in main thread

    def start(self, **kwargs):
        return self.parent.run_stream(self, run_in_main_thread=False, **kwargs)

    def evaluate(self, **kwargs):
        return self.parent.evaluate(self, run_in_main_thread=True, **kwargs)

    def train(self, **kwargs):
        return self.parent.train(self, run_in_main_thread=True, **kwargs)

    def infer(self, **kwargs):
        return self.parent.infer(self, run_in_main_thread=True, **kwargs)

    def stop(self):
        if self.status == 'stopped':
            return
        del self._inited_modules  # 引用计数置0，释放内存
        self._inited_modules = collections.OrderedDict()
        self.status = 'stopped'  # 设置成stopped后, self.modules的值就是未出初始化过的模型了
