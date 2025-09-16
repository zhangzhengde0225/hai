import os

from .configs import CONST
from .apis import __version__, __author__, __appname__, __email__, __affiliation__, __version_suffix__
from .version import __url__
from .apis import AbstractInput, AbstractModule, AbstractOutput, AbstractQue
from .apis import MODULES, SCRIPTS, IOS, init_register
from .apis import Config
from .apis import UAII, uaii, cli
from .apis import hub
# from .apis import hai_config as config  # inclue hai root_path, weights_root and other configs
from .apis import grpc_secure_server
from .apis import Testor
from .apis import argparse, parse_args_into_dataclasses, parse_args
from .apis import general
from .apis import worker, BaseWorkerModel, WorkerArgs

# LLM
from .apis import LLM, Model, Models, api_key
# from .apis import HepAI
# from .uaii.hepai_object import (
#     HepAI, HaiCompletions, ChatCompletion, ChatCompletionChunk, Stream
#     )
from .uaii.utils.file_object import HaiFile
from .configs import CONST


# from xsensing_ai.modules import *  # 加载项目的模块
# from xsensing_ai.uaii.server.grpc.grpc_xai_client import XAIGrpcClient

# from . import nn

# """
# 导入内部模块和外部模块
internal_modules = [
    'hai/apis/modules/YOLOv5',
    'hai/apis/modules/ResNet',
    # 'hai/apis/modules/UNet',
    'hai/modules/loader/images_loader',
    'hai/modules/exporter/images_exporter',
]
external_folders = [
    # '~/VSProjects/particle_transformer',
    # '~/VSProjects/FINet',
    'repos']

# if config.API_FOLD_NAME in os.listdir('.'):
if CONST.API_FOLD_NAME in os.listdir('.'):
    external_folders.insert(0, f'{os.getcwd()}')

init_register(internal_modules=internal_modules, external_folders=external_folders)
# """



