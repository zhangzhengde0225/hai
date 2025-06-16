import os, sys
from pathlib import Path
from hai.version import __appname__

# /home/xxx/VSProjects/hai
ROOT_PATH = f'{Path(os.path.abspath(__file__)).parent.parent.parent.parent}'  

# /home/xxx/.hai/weights
WEIGHTS_ROOT = f'{Path.home()}/.{__appname__}/weights' 

# /home/xxx/.hai/datasets
DATASETS_ROOT = f'{Path.home()}/datasets/{__appname__}_datasets'

# hai_api
API_FOLD_NAME = f'{__appname__}_api'

