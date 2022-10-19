"""
functions of hai datasets hub
"""
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent

import json
import shutil
import damei as dm


from .dataset_utils import get_file, extract_archive
from ..utils import general

class DatasetsHub(object):
    def __init__(self) -> None:
        self.urls = f'{pydir.parent.parent}/configs/urls/datasets.json'
        self._dataset_names = None
        self._datasets_dict = None
        self._init()

    def _init(self):
        with open(self.urls, 'r') as f:
            data = json.load(f)
        
        self._datasets_dict = data
        self._dataset_names = list(self._datasets_dict.keys())

    @property
    def names(self):
        return self._dataset_names

    @property
    def datasets(self):
        return self._datasets_dict

    @property
    def datasets_dict(self):
        return self._datasets_dict
    

    def __call__(self, *args, **kwargs):
        pass

    def list(self, **kwargs):
        ret_fmt = kwargs.get('ret_fmt', None)
        if ret_fmt is None:
            info = dm.misc.dict2info(self.datasets)
        elif ret_fmt == 'json':
            info = json.dumps(self.datasets, indent=4)
        elif ret_fmt == 'dict':
            info = self.datasets
        else:
            raise ValueError(f'Unsupported ret_fmt: {ret_fmt}')
        return info

    def list_remote_datasets(self, **kwargs):
        return self.list(**kwargs)

    def list_local_datasets(self, **kwargs):
        ret_fmt = kwargs.get('ret_fmt', 'dict')
        from ...apis import hai_config
        dset_root = hai_config.DATASETS_ROOT
        dsets = [x for x in os.listdir(dset_root) if os.path.isdir(os.path.join(dset_root, x))]
        if ret_fmt == 'list':
            return dsets
        elif ret_fmt == 'dict':
            ret_dict = {f'Total {len(dsets)} datasets': dsets}
            return ret_dict
        else:
            raise ValueError(f'Unsupported ret_fmt: {ret_fmt}')
    

    def download(self, *args, **kwargs):
        name = kwargs.get('name', None)
        version = kwargs.get('version', None)
        save_dir = kwargs.get('save_dir', '.')
        extract = kwargs.get('extract', False)
        force_download = kwargs.get('force_download', False)
        hash_algorithm = kwargs.get('hash_algorithm', 'md5')
        archive_format = kwargs.get('archive_format', 'auto')

        assert name is not None, 'dataset name is required, like: "hai datasets download SFID:latest"'
        name = name.lower()
        if ":" in name:
            name, version = name.split(":")
        version = version if version else 'latest'

        version = general.latest2determined(self.datasets_dict, name=name) if version == 'latest' else version

        # macth dataset by name and version
        data_entry = general.dict_match_item(self.datasets_dict, name=name, version=version)
        # print('entry: ', data_entry)
        origin = data_entry['url']
        fname = data_entry['name']
        file_hash = data_entry['md5'] if 'md5' in data_entry else None
        
        f_path, success = get_file(
            origin=origin,
             fname=fname,
             file_hash=file_hash,
             datadir=save_dir,
             hash_algorithm=hash_algorithm,
             extract=extract,
             force_download=force_download,
             archive_format=archive_format
           ) 
        return f_path, success
        
    def download_dataset(dataset, tp, envfile, force_download):
        """deprecated"""
        # info = datasets[dataset]
        basedir = tp
        datadir = os.path.join(basedir, dataset)
        if force_download:
            if os.path.exists(datadir):
                print(f'Removing existing dir {datadir}')
                shutil.rmtree(datadir)
        for subdir, flist in info.items():
            for url, md5 in flist:
                fpath, download = get_file(url, datadir=datadir, file_hash=md5, force_download=force_download)
                if download:
                    extract_archive(fpath, path=os.path.join(datadir, subdir))

        datapath = f'DATADIR_{dataset}={datadir}'
        with open(envfile) as f:
            lines = f.readlines()
        with open(envfile, 'w') as f:
            for l in lines:
                if f'DATADIR_{dataset}' in l:
                    l = f'export {datapath}\n'
                f.write(l)
        print(f'Updated dataset path in {envfile} to "{datapath}".')


if __name__ == '__main__':
    haid = DatasetsHub()
    print(haid.urls)

    info = haid.list()
    print(info)

    # haid.download_datsets('FINet')
    haid.download(name = 'SFID:latest')

