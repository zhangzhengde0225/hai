import os, sys
from pathlib import Path
from hai.version import __appname__

ROOT_PATH = f'{Path(os.path.abspath(__file__)).parent.parent.parent.parent}'  # /home/xxx/VSProjects/hai
WEIGHTS_ROOT = f'{os.environ["HOME"]}/.{__appname__}/weights'  # /home/xxx/.hai/weights
DATASETS_ROOT = f'{os.environ["HOME"]}/datasets/{__appname__}_datasets'  # /home/xxx/.hai/datasets
API_FOLD_NAME = f'{__appname__}_api'  # hai_api

