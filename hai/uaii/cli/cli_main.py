

import os, sys
import shutil

import argparse

import damei as dm
import hai
from ..utils.config_loader import PyConfigLoader as Config
from ...testor import Testor
from .cli_functions import CLIFunctions

logger = dm.getLogger('hai_cli')


def run():
    args = argparse.ArgumentParser()
    args.add_argument('mode', type=str, nargs='?', default=None, help='Operation, such as: list, download, train, eval, deploy, etc.')
    args.add_argument('sub_mode', type=str, nargs='?', default=None, help='Target, such as: <model_name>, <dataset_name>, remote, etc.')
    args.add_argument('sub_sub_mode', type=str, nargs='?', default=None, help='Additional parameter.')
    args.add_argument('-V', '--version', action='store_true', help='show version')
    args.add_argument('-f', '--force', action='store_true', help='force to run (if the api exists, clear it and init again)')
    opt = args.parse_args()

    cli = CommandLineInterface()
    cli(opt) 


class CommandLineInterface(CLIFunctions):
    def __init__(
        self, 
        uaii=None, 
        api_fold_name=None,
        root_path=None,
        ):
        self.uaii = uaii if uaii is not None else hai.UAII()
        self.api_fold_name = api_fold_name  # i.e. 'hai_api
        self.root_path = root_path  # i.e. '/home/xxx/VSProjects/hai'
        
        # self.config = config if config else hai.config # this is the hai config
        self.default_model = None  # if run hai command in a folder containing a model, then set the model as default model
        self.opt = None
        self.testor = Testor()
        
        
    
    def _init_opt(self, opt):
        # is cwd not in sys.path, then add it
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.append(cwd)

        # is_in_one_module = hai.config.API_FOLD_NAME in [x for x in os.listdir('.') if os.path.isdir(x)]
        is_in_one_module = self.api_fold_name in [x for x in os.listdir('.') if os.path.isdir(x)]
        if is_in_one_module:
            self.default_model = os.path.basename(os.getcwd())
        self.opt = opt
        return opt

    def __call__(self, opt, **kwargs):
        # print('opt: ', opt)
        opt = self._init_opt(opt)
        mode = opt.mode
        if mode == 'init':
            self._init_a_module(opt)  
        elif mode == 'list':
            self._deal_with_list(opt, **kwargs)
        elif mode == 'download':
            self._deal_with_download(opt, **kwargs)
        elif mode == 'model':
            self._deal_model_mode(opt)
        elif mode == 'models':
            self._list_all_modules(module=True)
        elif mode == 'weights':
            self._deal_weights_mode(opt)
        elif mode == 'datasets':
            self._deal_datasets_mode(opt)
        elif mode == 'test':
            self._deal_test_mode(opt)
        elif mode == 'train':
            self._deal_train_mode(opt)
        elif mode == 'version' or opt.version:
            self._show_version()
        elif mode == 'start':
            self._deal_with_start(**kwargs)
        elif mode is None:
            self._show_version()
            print(f'Please use "{hai.__appname__} -h" to see help.')
        else:
            exists_model_names = self.uaii.module_names
            if mode in exists_model_names:
                self._deal_exists_model(opt)
            else:
                raise NotImplementedError(f'Not implemented mode: {mode}')

    def _deal_exists_model(self, opt):
        model_name = opt.mode
        sub_mode = opt.sub_mode
        if sub_mode == 'configs':
            if not self.uaii.model:
                self.uaii.load_model(model_name)
            model = self.uaii.model
            assert self.uaii.model_name == model_name, f'Error: model_name: {model_name} != self.uaii.model_name: {self.uaii.model_name}'
            print(f'{model_name}: {model.config}')
            # self._list_all_modules(module=True)
        else:
            raise NotImplementedError(f'Not implemented sub_mode: {sub_mode}')

    def _deal_train_mode(self, opt):
        model_name = opt.sub_mode if opt.sub_mode else self.default_model
        # print(os.getcwd())
        model = self.uaii.load_model(model_name)
        model.train()

    
    def _deal_test_mode(self, opt):
        model_name = opt.sub_mode if opt.sub_mode else self.default_model
        ret = self.testor.test_module(model_name)
        # assert ret, f'Error: current test failed for module: {model_name}'

    def _deal_model_mode(self, opt):
        sub_mode = opt.sub_mode
        if sub_mode == 'list':
            self._list_all_modules(module=True)
        else:  # hai model 
            # current_model_name = self.uaii._model_name
            # print(f'Current_model_name: {current_model_name}')
            raise NotImplementedError(f'Not implemented sub_mode: {sub_mode}')
        
    def _deal_weights_mode(self, opt):
        opt = Config.from_argparse(opt)
        opt = opt.to_dict()
        _ = opt.pop('mode')
        model_name = opt.pop('sub_mode', None)
        weights = self.uaii.list_weights(model_name=model_name, **opt)
        print(f'Total {len(weights)} weights: {weights}')

    def _deal_datasets_mode(self, opt):
        sub_mode = opt.sub_mode
        ss_mode = opt.sub_sub_mode
        if sub_mode is None:  # list dataset in hai.DATASETS_ROOT
            info = self.uaii.list_datasets(sub_mode=sub_mode)
        # hai datasets list
        elif sub_mode == 'list':
            info = self.uaii.list_datasets(sub_mode=sub_mode, ret_fmt='dict')
            info = f'Total {len(info.keys())} datasets: {list(info.keys())}'
        elif sub_mode == 'info':
            info = self.uaii.list_datasets(sub_mode=sub_mode, ret_fmt='dict')
            info = dm.misc.dict2info(info) + \
            f'Total {len(info.keys())} datasets: {list(info.keys())}'
        elif sub_mode == 'download':  # download dataset
            info = self.uaii.download_dataset(name=ss_mode)
        else:
            if ss_mode == 'info':  # like: hai datasets SFID info
                dset_name = sub_mode.lower()
                ret = self.uaii.list_datasets(sub_mode='list', ret_fmt='dict')
                avail_datasets = list(ret.keys())
                if 'latest' in dset_name:  # like: hai datasets SFID:latest info
                    dset_name = dset_name.split(':')[0]
                    match = [x for x in avail_datasets if dset_name in x.lower()]
                    match = list(reversed(match))
                    if len(match) > 0:
                        versions = [ret[x]['version'] for x in match]
                        # print(f'Available versions: {versions}')
                        latest_version = sorted(versions)[-1]
                        dset_name = f'{dset_name}:{latest_version}'
                match = [x for x in avail_datasets if dset_name in x.lower()]
                # print(match)
                if len(match) > 0: 
                    info = {}
                    for x in match:
                        info[x] = ret[x]
                    info = f'{sub_mode} dataset info:\n'+dm.misc.dict2info(info)
                else:
                    raise NotImplementedError(f'Not implemented dataset: {sub_mode}, opt: {opt}')
            else:
                raise ValueError(f'sub_mode: {sub_mode} not supported. opt: {opt}')
        print(info)
        
        
    def _init_a_module(self, opt):
        # cfg = self.config
        # api_fold_name = cfg.API_FOLD_NAME  # i.e. 'hai_api
        # root_path = cfg.ROOT_PATH  # i.e. '/home/xxx/VSProjects/hai'
        
        api_fold_name = self.api_fold_name
        root_path = self.root_path

        if os.path.exists(api_fold_name):
            if not opt.force:
                logger.warning(f'API folder "{api_fold_name}" exists, please use "-f" to force to init again')
                return
            else:  # force
                pass
        else:                                                                                                                                                                                                                                                                                                                                                                                           
            os.mkdir(api_fold_name)

        cwd = os.getcwd()
        project_name = os.path.basename(cwd).lower()

        # Copy template files to api_fold
        shutil.copy(f'{root_path}/hai/apis/templates/README_template.md', 
                    f'{api_fold_name}/README.md')
        shutil.copy(f'{root_path}/hai/apis/templates/register_module_template.py', 
                    f'{api_fold_name}/{project_name}_api.py')
        shutil.copy(f'{root_path}/hai/apis/templates/init_template.py', 
                    f'{api_fold_name}/__init__.py')
        os.system(f'echo "\nfrom .{project_name}_api import *" >> {api_fold_name}/__init__.py')
        logger.info(f'Create API folder and files successfully: "{os.getcwd()}/{api_fold_name}"')


    def _show_version(self):
        data = dict()
        ver = hai.__version__ + '-' + hai.__version_suffix__
        data[f'{hai.__appname__.upper()} Version'] = ver
        # data['Author'] = hai.__author__
        data['URL'] = hai.__url__
        data['Contact'] = f'For any suggestions or demands, please email: {hai.__email__}'
        # print(f'HAI Version: {hai.__version__}, Author: {hai.__author__} @ {hai.__affiliation__}, Email: {hai.__email__}')
        info = dm.misc.dict2info(data)
        info = info[:-1] if info.endswith('\n') else info  # remove last \n
        print(info)

    def run(self):
        pass


