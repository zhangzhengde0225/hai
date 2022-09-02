"""
初始化注册，
在导入nn模块自动注册内部模块时，由于外部调用多次会导致对此初始化注册，仅初始化注册一次
"""
import os
import sys
from pathlib import Path


class InitRegister(object):
    def __init__(self, internal_dir=None):
        self.inited = False
        self.internal_dir = internal_dir  # /home/zzd/VSProject/hai/hai

    def import_internal_module(self, internal_module_path):
        """
        导入内部模块
        :param internal_module_path: internal module path, e.g.: apis/modules/YOLOv5-v6
        """
        if self.internal_dir is None:
            full_path = os.path.join(os.getcwd(), internal_module_path)
        else:
            full_path = os.path.join(self.internal_dir, internal_module_path)  # /home/zzd/VSProject/hai/hai/apis/modules/YOLOv5_v6
        full_path = Path(full_path)
        # dir_path = str(full_path.parent)
        # stem = str(full_path.stem)

        xx = internal_module_path.split('/')
        xx = '.'.join(xx)

        code = f'from {xx} import __init__'
        exec(code)


    def __call__(self, internal_modules, external_folders):
        """
        初始化注册
        :param internal_modules: internal modules, e.g: models/loader/vis_loader
        :param external_folders: external folders, e.g.: dmapi, repos
        """
        if self.inited:
            pass
        else:
            # print(self.inited)
            ims = internal_modules
            efs = external_folders  # ['dmapi', 'repos']
            if len(ims) > 0:
                for i, im_path in enumerate(ims):
                    self.import_internal_module(im_path)

            if len(efs) > 0:
                dirs = [x for x in os.listdir('.') if os.path.isdir(x)]  # 当前路径文件夹
                for dmp in dirs:
                    if dmp in efs:
                        # code = f'from repos.xxx.dmapi import *'
                        code = f'from {dmp} import *'
                        exec(code)
            self.inited = True

