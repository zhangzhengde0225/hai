"""
模块的io，模块有输入流和输入流，每个流都有队列
"""
import os, sys
import time
import damei as dm
# from ..registry import MODULES, SCRIPTS, IOS
from damei.nn.api.registry import MODULES, SCRIPTS, IOS
from damei.nn.uaii.stream.base_input import AbstractInput


# @IOS.register_module(name='visible_input')
class VisInputStream(AbstractInput):
    """
    iterable data_loader
    use:
        data_loader = VisInputStream(data_path, batch_size, shuffle=True)
        for i, demo_for_dm.data in enumerate(data_loader):
            print(demo_for_dm.data)
    """

    name = 'visible_input'
    status = 'stopped'
    description = '可见光数据输入流'

    def __init__(self, m_cfg, *args, **kwargs):
        self.m_cfg = m_cfg  # 自己所属模块的配置
        self.cfg = m_cfg.input  # 自己的cfg
        que = self.cfg.get('que', None)
        super(VisInputStream, self).__init__(que=que, *args, **kwargs)
