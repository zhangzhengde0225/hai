

import os, sys
from pathlib import Path    
here = Path(__file__).parent
from ..version import __appname__

# /home/xxx/VSProjects/hai
ROOT_DIR = here.parent.parent
ROOT_PATH = ROOT_DIR

# /home/xxx/.hepai/weights
WEIGHTS_ROOT = f'{Path.home()}/.{__appname__}/weights'

# /home/xxx/.hepai/datasets
DATASETS_ROOT = f'{Path.home()}/.{__appname__}/datasets'

# hai_api
API_FOLD_NAME = f'{__appname__}_api'
