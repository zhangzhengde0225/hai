from .registy import Registry
from .init_register import InitRegister

# print('registry init')

MODULES = Registry('module', build_func=None)
SCRIPTS = Registry('script', build_func=None)
# STREAMS = Registry('stream', build_func=None)
IOS = Registry('io', build_func=None, id_prefix='IO')

init_register = InitRegister()
