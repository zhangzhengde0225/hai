
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent
import json

import damei as dm

logger = dm.get_logger('ModelHub')

class ModelHub(object):

    def __init__(self) -> None:
        self.urls = f'{pydir.parent}/configs/urls/hub_models.json'
        self._keys = None  # i.e model names
        self._items = None  # i.e model dict

    def _read_json(self):
        with open(self.urls, 'r') as f:
            data = json.load(f)
        self._keys = list(data.keys())
        self._items = data
        return data

    @property
    def keys(self):
        if self._keys is None:
            self._read_json()
        return self._keys

    @property
    def items(self):
        if self._items is None:
            self._read_json()
        return self._items

    def list_remote_models(self, **kwargs):
        """按类别统计"""
        info = {}
        for k, v in self.items.items():
            name = k  # i.e. model name
            category = v['category']  # i.e. model category
            if category not in info.keys():
                info[category] = [name]
                continue
            info[category].append(name)
        return info

    def download(self, *args, **kwargs):
        name = kwargs.get('name', args[0])
        url = self.items[name]['url']
        
        code = f'git clone {url}'
        logger.info(f'Run code: {code}')
        os.system(code)
        

