"""
damei nn api for ai algorithm management (unified ai interface)
"""

from .base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from .registry import MODULES, SCRIPTS, IOS, init_register
from .utils import Config
from damei.nn.uaii.uaii_main import UAII

from damei.nn.test import test_module, test_script, test_io
