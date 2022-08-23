from .base_queue import AbstractQue


class AbstractInput(object):  # 定义它是一个可遍历的对象
    name = 'default_input_name'
    status = 'stopped'
    description = 'default_input_description'

    def __init__(self, *args, **kwargs):
        que = kwargs.pop('que', None)
        if que:
            maxlen = que.get('maxlen', 5)
            self.que = AbstractQue(maxlen, *args, **kwargs)
        else:
            self.que = None

        self._attrs = []
        self._items = dict()

        self.data = None

    @property
    def attrs(self):
        return self._attrs

    @property
    def items(self):
        return self._items

    def _init_from_PyConfigLoader(self, cfg):
        """支持dm.nn.api.Config类型的参数配置"""
        assert 'input' in cfg.keys()
        input_cfg = cfg['input']
        self._items = input_cfg
        # print(input_cfg, type(input_cfg))
        # for k, v in input_cfg.items():
        #     assert isinstance(k, str)
        #     if k not in self.attrs:
        #         self._attrs.append(k)
        #     if hasattr(self, k):
        #         delattr(self, k)
        #     setattr(self, k, v)
        #
        # print(self.attrs)
        # print(self.items)

    def __len__(self):
        return len(self.data)

    def __next__(self):
        return self.data.__next__()

    def __iter__(self):

        return self.data.__iter__()