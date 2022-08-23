"""
为了任意路径下的.py包的引入
"""
import os, sys
from pathlib import Path
import damei as dm

logger = dm.getLogger('arbitray_import')


def arbitrary_import(path):
    logger.warn(f'Not tested.')
    if os.path.isdir(path):
        path = f'{path}/__init__.py'
    abs_path = Path(os.path.abspath(path))
    cdir = os.getcwd()  # 当前工作目录
    sys.path.append(f'{abs_path.parent}')
    module_dir = '.'
    os.chdir(f'{abs_path.parent}')  # 切换工作目录
    code = f'import {abs_path.stem}'

    try:
        exec(code)
    except Exception as e:
        msg = f'Error in "exec(code)": {e}. Error variables:\n' \
              f'    abs path: {abs_path} \n' \
              f'    code: {code} \n' \
              f'    module dir: {module_dir} \n' \
              f'    sys.path[-1]: {sys.path[-1]} '
        raise Exception(msg)

    sys.path = sys.path[:-1:]
    os.chdir(cdir)
