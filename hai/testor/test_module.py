# coding=utf-8

import os, sys
from pathlib import Path
import hai

pydir = Path(os.path.abspath(__file__)).parent

try:
    import damei as dm
except:
    sys.path.append(f'{Path(pydir).parent}/damei')
    import damei as dm

logger = dm.getLogger('dm.nn.test')


class TestModule(object):
    def __init__(self):
        self.uaii = hai.UAII()
        self.current_model_name = None
        self._model = None
        self.test_items = ['init', 'train', 'infer', 'evaluate']
        self.test_results = {}

        # print(self.uaii.ps())

    @property
    def model(self):
        return self._model

    def __call__(self, model_name, *args, **kwargs):
        uaii = self.uaii
        logger.info(f'Staring module: "{model_name}" testing ...')
        self.try_test(model_name, *args, **kwargs)

        print(f'test_ret: {self.test_results}')
        
    def try_test(self, model_name, *args, **kwargs):
        all_models = hai.MODULES
        print(all_models)
        self.current_model_name = model_name

        # test init
        try:
            self.test_init(*args, **kwargs)
            self.test_results['init'] = 'Passed'
        except Exception as e:
            self.test_results['init'] = f'Failed with error: {e}'
            raise e

        # test train
        try:
            self.test_train(*args, **kwargs)
            self.test_results['train'] = 'Passed'
        except Exception as e:
            self.test_results['train'] = f'Failed with error: {e}'
            raise e


    def test_train(self):
        model = self.model
        model.train()

    def test_init(self):
        # test model load
        model = self.uaii.load_model(self.current_model_name)
        print('model', model)
        # test config
        config = model.config
        print('config', config)
        self._model = model

    def test_module(self, m_name, **kwargs):
        uaii = self.uaii
        logger.info(f'测试模块{m_name}初始化。')
        # module = uaii.get_module(name=m_name)()  # 获取并初始化
        stream = uaii.build_stream(m_name)
        return stream


    def x(self):
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


if __name__ == '__main__':
    tm = TestModule()
    tm()
