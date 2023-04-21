"""iniverse testor"""


# from hai.testor.test_module import TestModule


class Testor(object):
    def __init__(self) -> None:
        
        pass

    def __call__(self):
        pass

    def test_module(self, module_name, **kwargs):
        """entry function for algorithm module test"""
        from .test_module import TestModule
        t = TestModule()
        t(model_name=module_name, **kwargs)