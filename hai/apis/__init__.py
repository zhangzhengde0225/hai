"""
damei nn api for ai algorithm management (unified ai interface)
"""

import argparse
from ..version import __backend__, __version__, __author__, __appname__, __email__
from ..version import __affiliation__, __version_suffix__
import os, sys
from pathlib import Path

# damei.nn warpper
__pydir__ = Path(os.path.dirname(os.path.abspath(__file__)))

# 导入damei lib
try:
    import damei
except:
    sys.path.append(f'{__pydir__.parent.parent.parent}/damei')
    import damei

logger = damei.getLogger('hai')
# logger.info(f'HAI version: {__version__}')


if __backend__ == 'local':
    from .basic.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
    from .basic.registry import MODULES, SCRIPTS, IOS, InitRegister
    from .basic.utils import Config
    from .basic.grpc import grpc_secure_server
    from ..uaii.uaii_main import UAII
    from ..uaii.cli.cli_main import CommandLineInterface
    from ..testor import Testor
    from ..uaii.datasets.datasets_hub import DatasetsHub
    from .basic import argparse, parse_args_into_dataclasses, parse_args
    from ..uaii.utils import general
    from ..uaii.worker.worker import WorkerWarper as worker, WorkerArgs
    from ..uaii.worker.base_worker_model import BaseWorkerModel

elif __backend__ == 'damei':
    from damei.nn.api.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
    from damei.nn.api.registry import MODULES, SCRIPTS, IOS
    from damei.nn.api.utils import Config
    from damei.nn.api.utils import Config as PyConfigLoader
    from damei.nn.api import UAII as UAII
else:
    raise NotImplementedError(f'{__backend__} backend is not supported, only local and damei, please check')

from .workers_api.llm.llm import HaiLLM as LLM
from .workers_api.model import HaiModel as Model
from .workers_api.model import HaiModel as Models


# hai_config = Config(f'{__pydir__.parent}/configs/Base/hai_config.py')
# from ..configs.Base.hai_config import root_path, weights_root
# root_path = f'{Path(__pydir__).parent.parent}'

from ..configs import CONST

# init_register = InitRegister(internal_dir=hai_config.root_path)
init_register = InitRegister(internal_dir=CONST.ROOT_PATH)
uaii = UAII()
cli = CommandLineInterface(
    uaii=uaii, 
    api_fold_name=CONST.API_FOLD_NAME,
    root_path=CONST.ROOT_PATH,
    )
api_key = os.getenv('HEPAI_API_KEY')