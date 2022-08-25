"""
damei nn api for ai algorithm management (unified ai interface)
"""

from .basic.base import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from .basic.registry import MODULES, SCRIPTS, IOS, init_register
from .basic.utils import Config

from ..uaii.uaii_main import UAII

from ..tests.test import test_module, test_script, test_io
