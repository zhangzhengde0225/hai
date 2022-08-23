import os, sys
import numpy as np
import logging
from threading import Thread
import time
from pathlib import Path
import damei as dm

try:
    import eventlet
    # from .socket.server import SocketApp
except Exception as e:
    dm.EXCEPTION(Exception, e, mute=True)

from .utils.base_uaii import BaseUAII
from .stream.streams import Streams

try:
    from .. import MODULES, SCRIPTS, IOS
except:
    from damei.nn.api import MODULES, SCRIPTS, IOS

from .utils.config_loader import PyConfigLoader as Config

pydir = Path(os.path.abspath(__file__)).parent
# sys.path.append(f'{pydir.parent}')
# from modules import *  # 不能用from xsensing_ai.module import *，否则在pyconfigloader里会二次注册
logger = dm.getLogger('uaii_main')


class UAII(BaseUAII):
    """UAII: Unified AI Interface of damei.
    uaii = dm.nn.api.UAII()
    """

    def __init__(self, cfg=None, root_path=None, **kwargs):
        super(UAII, self).__init__(**kwargs)
        self.root_path = root_path if root_path else f'{pydir.parent.parent.parent}'
        cfg = cfg if cfg else f'{pydir.parent}/config/uaii_stream_config.py'
        self.cfg = Config(cfg_file=cfg, root_path=self.root_path)
        self._modules = MODULES  # 一个对象
        self._scripts = SCRIPTS
        self._ios = IOS
        self._configure()
        # print(self.modules)
        self._streams = self.init_streams(cfg=self.cfg)
        # print(self.streams)
        # self.configure()
        self._name2cls = self.register_name2cls()  # 记录模块名和它注册到了那个模块中

    def __call__(self, *args, **kwargs):
        pass

    def init_streams(self, cfg):
        return Streams(cfg, parent=self)

    def run_xxx_deprecated(self):
        """配置管道、初始化、运行流
        :param name:
        :param pipe: 指定管道，None是默认运行全部。
        """
        uaii_cfg = self.cfg

        streams = [x for x in uaii_cfg.enable_streams if x in uaii_cfg.streams.keys()]  # 默认全部

        # 为每个流配置管道，运行流，一个管道有多个模块，每个模块可视为一截管道
        running_modules = {}  # 已经运行的模块
        for i, stream in enumerate(streams):
            stream_cfg = uaii_cfg.streams[stream]  # list, 元素长度是模块数目，前一个模块的输入是后一个模块的输出
            module_names = [x['type'] for x in stream_cfg]

            # module = None
            last_mo = None
            for j, mname in enumerate(module_names):
                mtask = stream_cfg[j].get('task', None)
                print(f'running: {mname:<15} task: {mtask if mtask else "None":<6} last mo: {last_mo}')
                if f'{mname} {mtask}' in running_modules.keys():
                    last_mo = running_modules[f'{mname} {mtask}'].mo
                    continue
                mi = None if j == 0 else last_mo  # 模块输入
                run_in_main_thread = False if mname == 'deepsort' else False
                module = self.configure_and_run_module(
                    module=mname, mtask=mtask, mi=mi,
                    run_in_main_thread=run_in_main_thread,
                )
                running_modules[f'{mname} {mtask}'] = module
                last_mo = module.mo

        # self.fetch(running_modules['deepsort infer'].mo)

        done = True
        if done:
            print(f'done')
        return done

    def fetch(self, stream):
        """输出流"""
        fetch_times = 1
        while True:
            t0 = time.time()
            if len(stream.que):
                data = stream.get_last()
                # demo_for_dm.data = stream.scan()
                print(f'fetch times: {fetch_times} que lenth: {len(stream.que)}'
                      f' demo_for_dm.data: {data[:3]}', end='')
                fetch_times += 1
                print(f' {(time.time() - t0) * 1000:.6f} ms')
            time.sleep(0.0001)
        print('')

    def start(self, stream=None, module=None):
        """开始运行某些模块/流"""
        # print(stream, module)
        ps = self.ps()
        print(ps)
        return self.run()

    def stop(self, stream=None, pipeline=None, module=None):
        """停止指定模块或停止所有模块"""
        logger.info('stop stream pipeline module')

        print(stream, pipeline, module)
        exit()

    def build_io_instance(self, io_type, m_cfg):
        """
        构建io实例
        :param io_type: input/output
        :param m_cfg: module config
            for example:
                dict(
                    type='visible_input',
                    enable=True,
                    source='/path/to/demo_for_dm.data',
                    ...,
                )
        :return: i/o instance from self._ios
        """
        if io_type in ['input_stream', 'output_stream']:
            raise NotImplementedError(f'{io_type} not implemented')

        m_io_stream_cfg = m_cfg.get(io_type, None)
        if not m_io_stream_cfg:
            return None

        module_name = m_io_stream_cfg['type']
        if module_name is None:
            return None
        enabled = m_io_stream_cfg.get('enabled', True)
        if not enabled:
            return None
        io = self.get_module(name=module_name)  # input or output
        # print(f'{io_type} module: {module_name} m_cfg: {m_cfg}')
        io = io(mcfg=m_cfg)
        return io

    def run(self, stream, **kwargs):
        return self.run_stream(stream, run_in_main_thread=True, **kwargs)

    def start_stream(self, stream, **kwargs):
        # is_req = kwargs.get('is_req', False)
        return self.run_stream(stream, run_in_main_thread=False, **kwargs)

    def run_stream(self, stream, **kwargs):
        """
        运行流
        :stream: 可以是stream_name，也可以是一个对象
        :return:
        """
        # 读取参数
        run_in_main_thread = kwargs.pop('run_in_main_thread', True)  # 是否在主进程运行
        mtask = kwargs.pop('task', 'infer')  # 任务：infer/train/evaluate
        stream_cfg = kwargs.pop('stream_cfg', None)  # 流配置
        is_req = kwargs.pop('is_req', False)  # 是否是请求
        # mi = kwargs.get('mi', None)
        # mo = kwargs.get('mo', None)

        # 读取流
        stream = self.get_stream(name=stream) if isinstance(stream, str) else stream
        # logger.info(f'Run stream "{stream.name}", params: {kwargs}.')

        # 初始化流
        if stream.status == 'stopped' or stream_cfg is not None:
            stream.init(stream_cfg=stream_cfg)  # stream_cfg不为None时，会强制初始化

        last_generator = None
        for i, (mname, m) in enumerate(stream.models.items()):
            is_first = i == 0
            is_last = i == (len(stream.models))
            # mname = module['type']
            # m = stream.modules[mname]
            # print(f'm status: {m.status}')
            assert m.status == 'ready', f'Status of "{mname}" must be "ready" rather than "{m.status}".'

            if m.status == 'running':
                logger.warn(f'Module: {mname} already run, specify "force=True" if you want to stop and run.')
                # TODO: force run_stream
                last_generator = None
                continue

            logger.info(f'Run module: {mname} mtask: {mtask} main_thread: {run_in_main_thread}')
            # 处理模块的mi
            if not is_first:  # 非第1个模块，用上一个模块的输出来覆盖mi
                # print(f'last_generator: {last_generator}')
                m.mi = last_generator
            result = self.run_module(m=m, mtask=mtask, run_in_main_thread=run_in_main_thread, **kwargs)
            # 返回值是generator，是一个生成器
            last_generator = result

        if is_req:
            if last_generator:
                return 1, f'Successfully run stream {stream.name}.'
            else:
                return 0, f'Run stream {stream.name} failed.'
        return last_generator

    def run_module(self, m, mtask=None, mi=None, mo=None, daemon=True, run_in_main_thread=False, **kwargs):
        """
        run module in stream.
        return: iterable result object if run in main thread, True/False if run in thread
        """
        if run_in_main_thread:
            retsult = self.run_module_in_main_thread(m, mtask, **kwargs)
            return retsult

        else:
            # 不指定任务时，调用call函数
            if mtask is None:
                thread = Thread(
                    target=m.__call__,
                    daemon=daemon, )
            # 推理任务
            elif mtask == 'infer':
                thread = Thread(target=m.infer, kwargs={'mi': mi, "mo": mo}, daemon=True)
            # 训练任务
            elif mtask == 'train':  # TODO
                thread = None
                m.train()
            # 评估任务
            elif mtask == 'evaluate':
                thread = None
                m.test()
            else:
                raise KeyError(f'uaii module task error. module: {m} task: {mtask}.')

            # 启动线程
            thread.start()

        return True

    def run_module_in_main_thread(self, m, mtask, **kwargs):
        """在主进程跑任务"""
        # print(f'run: {m} {mtask} {mi} {mo}')
        # 调用call
        if mtask is None:
            return m.__call__()
        # 推理任务
        elif mtask == 'infer':
            result = m.infer(**kwargs)
        # 训练任务
        elif mtask == 'train':  # TODO
            result = m.train(**kwargs)
        # 评估任务
        elif mtask == 'evaluate':
            # result = 0
            result = m.evaluate(**kwargs)
            # m.status = 'stopped'
        else:
            raise KeyError(f'uaii module task error. module: {m} task: {mtask}.')

        m.status = 'ready'
        return result

    def evaluate(self, stream, **kwargs):
        """评估某个单模块组成的流"""
        stream_name = stream if isinstance(stream, str) else stream.name
        stream_cfg = kwargs.get('cfg', None)
        # print(stream_cfg)
        logger.info(f'Evaluate monoflow: {stream_name}.')
        # cfg = kwargs.get('cfg', None)
        # print(cfg)
        result = self.run_stream(stream=stream, task='evaluate', stream_cfg=stream_cfg, **kwargs)
        return result
        # return self.run_stream(monoflow, **kwargs)

    def train(self, stream, **kwargs):
        stream_name = stream if isinstance(stream, str) else stream.name
        stream_cfg = kwargs.get('cfg', None)
        logger.info(f'Train monoflow: {stream_name}.')
        result = self.run_stream(stream=stream, task='train', stream_cfg=stream_cfg, **kwargs)
        return result

    def infer(self, stream, **kwargs):
        stream_name = stream if isinstance(stream, str) else stream.name
        stream_cfg = kwargs.get('cfg', None)
        logger.info(f'Infer monoflow: {stream_name}.')
        result = self.run_stream(stream=stream, task='infer', stream_cfg=stream_cfg, **kwargs)
        return result


def main(root_path):
    logger = logging.getLogger('uaii')
    print(f'root_path: {os.path.abspath(root_path)}')
    cfg = f'{root_path}/config/uaii_stream_config.py'
    uaii = UAII(cfg=cfg, root_path=root_path)
    # uaii.moduels.build()

    # 查看注册了的模块
    ps_info = uaii.ps()
    print(f'ps_info: \n{ps_info}')
    exit()

    # 根据配置文件，配置模块的连接关系，并初始化
    uaii.run()  # 根据配置文件运行多个管道

    print(f'modules: {uaii.modules}')
    print(f'module scope: {uaii.modules.scope}')

    # 查看注册了的模块
    ps_info = uaii.ps()
    print(f'ps_info: \n{ps_info}')

    # print(f'ms: {type(ms)} {ms}')
    # ret = ms.inference()
    # print(f'ms ret: {ret}')

    pass


def run_app(root_path):
    # build app
    logger = logging.getLogger('uais')
    cfg = f'{root_path}/config/uaii_stream_config.py'
    uaii = UAII(cfg=cfg)
    SocketApp.uaii = uaii  # 设置socket app的unified ai service
    socket_app = SocketApp()
    # app.logger.info('socket app加载完成')
    eventlet.wsgi.server(eventlet.listen(('', 5000)), socket_app.app)
