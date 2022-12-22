"""
TODO 2022.12.06
"""

import os


class Trainer(object):
    """
    hai trainner训练器
    1.收集信息：模型、数据加载器、输出器、优化器、
    2.面向切面的训练器    
    """
    
    def __init__(self, model, **kwargs):
        self.model = model
        self.kwargs = kwargs
        

    def train(self):

        for i, data in enumerate(self.model.train_loader):
            print(i, data)
