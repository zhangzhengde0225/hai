"""
初始化注册，
在导入nn模块自动注册内部模块时，由于外部调用多次会导致对此初始化注册，仅初始化注册一次
"""
import damei as dm
import os
import sys
from pathlib import Path

logger = dm.get_logger('init_register')


class InitRegister(object):
    def __init__(self, internal_dir=None, api_fold_name='hai_api'):
        self.inited = False
        self.internal_dir = internal_dir  # /home/zzd/VSProject/hai/hai
        self.api_fold_name = api_fold_name
        self.show_logger = False

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

        imp = internal_module_path.split('/')
        imp = '.'.join(imp)

        # print('import_internal_module', imp)

        code = f'from {imp} import __init__'
        self.exec_import(code, internal_module_path)
        
    
    def import_external_module(self, external_module_path):
        """
        导入外部模块
        :param external_module_path: external module path, e.g.: repos/xxx/hai_api
        """
        emp = external_module_path
        if emp.startswith('~'):
            emp = emp.replace('~', str(Path.home()))
        emp = os.path.abspath(emp) 
        if not os.path.exists(os.path.join(emp, self.api_fold_name)):
            if self.show_logger:
                logger.warn(f'External module path "{emp}" not exists, and will be ignored.')
            return

        emp = os.path.join(emp, self.api_fold_name)
        # judge if the external module is a python package
        if not os.path.exists(os.path.join(emp, '__init__.py')):
            if self.show_logger:
                logger.warn(f'External module "{emp}" is not a python package, and will be ignored.')
            return
        # print('import_external_module', emp)
        
        self.import_init(emp)
                
        
    def import_init(self, path):
        # print(f'sys.path: {sys.path}')
        for p in sys.path:
            if p == '':
                continue
            elif p == path:
                package, name = '.', '__init__'
                code = f'from {package} import {name}'
                self.exec_import(code, package)
                return
            elif p in path:  # sys.path in input path, i.e. /home/zzd/VSProjects/hai in /home/zzd/VSProjects/hai/hai_api
                # print(f'sys.path in input path: p: {p} path: {path}')
                package = path.replace(p, '')
                package = '.'.join(package.split('/'))
                package = package[1:] if package.startswith('.') else package
                name = '__init__'
                code = f'from {package} import {name}'
                self.exec_import(code, package)
                return
            else:
                continue
        
        # print('import_init xx')
        # no env availabel i.e. /home/zzd/VSProjects/particle_transformer 
        # need add path to sys.path

        # Debug 01: Two modules with the same api_fold_name "hai_api", and only one will be registered.'
        #    Solve: change stem to project_name/stem, e.g. particle_transformer/hai_api, and the package name is shortten
        #    20220926: Unsolved.

        # dir = f'{Path(path).parent.parent}'
        dir = f'{Path(path).parent}'
        # dir = path
        stem = os.path.basename(path)
        cwd = os.getcwd()
        sys.path.insert(0, dir)
        os.chdir(dir)
        # package, name = f'{Path(path).parent.stem}/{stem}', '__init__'
        package, name = f'{stem}', '__init__'
        code = f'from {package} import {name}'
        # code = 'from . import *'
        # print('import_init', code, sys.path)
        self.exec_import(code, dir)
        os.chdir(cwd)  
        sys.path.pop(0)
        return

    def exec_import(self, code, path):
        """
        执行导入
        :param code: import code
        :param path: import path
        """
        if self.show_logger:
            logger.info(f'Internal module "{path}" registered.')
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
                # print(efs)
                # support external folders
                for i, ef in enumerate(efs):
                    self.import_external_module(ef)

                # dirs = [x for x in os.listdir('.') if os.path.isdir(x)]  # 当前路径文件夹
                # for dmp in dirs:
                #     if dmp in efs:
                #         # code = f'from repos.xxx.dmapi import *'
                #         code = f'from {dmp} import *'
                #         exec(code)
            self.inited = True

