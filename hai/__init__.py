

from .apis import AbstractInput, AbstractModule, AbstractOutput, AbstractQue
from .apis import MODULES, SCRIPTS, IOS, init_register
from .apis import Config
from .apis import UAII, uaii
from .apis import hub
from .apis import root_path

# from xsensing_ai.modules import *  # 加载项目的模块
# from xsensing_ai.uaii.server.grpc.grpc_xai_client import XAIGrpcClient



# """
# 导入内部模块和外部模块
internal_modules = [
    'hai/apis/modules/YOLOv5',
    'hai/apis/modules/ResNet',
    'hai/apis/modules/UNet',
    'hai/modules/loader/images_loader',
    'hai/modules/exporter/images_exporter',
]
external_folders = ['dmapi', 'repos']

init_register(internal_modules=internal_modules, external_folders=external_folders)
# """



