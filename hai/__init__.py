import os, sys
from telnetlib import PRAGMA_HEARTBEAT
from .version import __backend__, __version__

# 导入damei lib
try:
    import damei
except:
    import os, sys
    from pathlib import Path

    # damei.nn warpper
    __pydir__ = Path(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(f'{__pydir__.parent}/damei')
    import damei

# print(damei)
logger = damei.getLogger('hai')
logger.info(f'HAI version: {__version__}')


if __backend__ == 'local':
    from .apis import AbstractInput, AbstractModule, AbstractOutput, AbstractQue
    from .apis import MODULES, SCRIPTS, IOS, init_register
    from .apis import Config
    from .apis import UAII
    from .apis import hub
elif __backend__ == 'damei':
    from damei.nn.api.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
    from damei.nn.api.registry import MODULES, SCRIPTS, IOS
    from damei.nn.api.utils import Config
    from damei.nn.api.utils import Config as PyConfigLoader
    from damei.nn.api import UAII as UAII
else:
    raise NotImplementedError(f'{__backend__} backend is not supported, only local and damei, please check')

# from xsensing_ai.modules import *  # 加载项目的模块
# from xsensing_ai.uaii.server.grpc.grpc_xai_client import XAIGrpcClient

# """
# 导入内部模块和外部模块
internal_modules = [
    'apis/modules/YOLOv5_v6',
    'apis/modules/ResNet',
    'modules/loader/images_loader',
    'modules/exporter/images_exporter',
]
external_folders = ['dmapi', 'repos']

init_register(
    internal_modules=internal_modules,
    external_folders=external_folders
)
# """





