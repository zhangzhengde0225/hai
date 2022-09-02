"""
damei nn api for ai algorithm management (unified ai interface)
"""

from ..version import __backend__, __version__
import os, sys
from pathlib import Path

# damei.nn warpper
__pydir__ = Path(os.path.dirname(os.path.abspath(__file__)))

# 导入damei lib
try:
    import damei
except:
    sys.path.append(f'{__pydir__.parent}/damei')
    import damei

logger = damei.getLogger('hai')
logger.info(f'HAI version: {__version__}')


if __backend__ == 'local':
    from .basic.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
    from .basic.registry import MODULES, SCRIPTS, IOS, init_register
    from .basic.utils import Config
    from ..uaii.uaii_main import UAII
    from ..tests.test import test_module, test_script, test_io

elif __backend__ == 'damei':
    from damei.nn.api.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
    from damei.nn.api.registry import MODULES, SCRIPTS, IOS
    from damei.nn.api.utils import Config
    from damei.nn.api.utils import Config as PyConfigLoader
    from damei.nn.api import UAII as UAII
else:
    raise NotImplementedError(f'{__backend__} backend is not supported, only local and damei, please check')

root_path = f'{Path(__pydir__).parent.parent}'
uaii = UAII()