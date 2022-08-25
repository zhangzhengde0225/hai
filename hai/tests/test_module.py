#!/home/zzd/anaconda3/envs/yolov5/bin/python
# coding=utf-8

import os, sys
from pathlib import Path
import inspect

pydir = Path(os.path.abspath(__file__)).parent
cdir = os.getcwd()
# 检查是否有dmapi
dirs = [x for x in os.listdir('.') if os.path.isdir(x)]
if 'dmapi' not in dirs:
    raise NotADirectoryError(
        f'Please run this tool on the directory which contains the "dmapi" fold. '
        f'Your can refer to the damei doc for configuration method.',
    )
if cdir not in sys.path:  # 添加当前路径，以便能from dmapi import *
    sys.path.append(f'{cdir}')
try:
    import damei as dm
except:
    sys.path.append(f'{Path(cdir).parent}/damei')
    import damei as dm

logger = dm.getLogger('dm.nn.test')


class TestModule(object):
    def __init__(self):
        self.uaii = dm.nn.UAII()

        print(self.uaii.ps())

    def __call__(self, *args, **kwargs):
        uaii = self.uaii
        ms = uaii.modules.module_dict  # modules
        mnames_under_cdir = [k for k, v in ms.items() if inspect.getfile(v).startswith(f'{cdir}')]

        for m_name in mnames_under_cdir:
            stream = self.test_module(m_name)  # 测试初始化
            ret = self.test_train(stream)

    def test_module(self, m_name, **kwargs):
        uaii = self.uaii
        logger.info(f'测试模块{m_name}初始化。')
        # module = uaii.get_module(name=m_name)()  # 获取并初始化
        stream = uaii.build_stream(m_name)
        return stream

    def test_train(self, stream):
        ret = stream.run(task='train')
        return ret


if __name__ == '__main__':
    tm = TestModule()
    tm()
