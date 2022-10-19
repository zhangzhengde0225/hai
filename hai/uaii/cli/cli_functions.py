import damei as dm
import hai

class CLIFunctions(object):

    def _deal_with_list(self, *args, **kwargs):
        """mode = list"""
        opt = self.opt
        sub_mode = opt.sub_mode
        ss_mode = opt.sub_sub_mode
        # hai list
        if sub_mode is None:
            info = self.uaii.ps(**kwargs)
        elif sub_mode == 'remote':  
            # hai list remote
            # hai list remote models
            if ss_mode is None or ss_mode in ['model', 'models']: 
                dict_info = self.uaii.list_remote_models()
                info = dm.misc.dict2info(dict_info)
            # hai list remote datasets
            elif ss_mode == 'datasets':
                dict_info = self.uaii.list_remote_datasets(sub_mode=sub_mode, ret_fmt='dict')
                # info = {}
                dict_info[f'Total {len(dict_info.keys())} datasets:'] = list(dict_info.keys())
                info = dm.misc.dict2info(dict_info)
        # hai list datasets
        elif sub_mode in ['datasets', 'dataset']:  # hai list datasets
            info = self.uaii.list_local_datasets()
            info = dm.misc.dict2info(info)
        else:
            raise NotImplementedError(f'Not implemented sub_mode: "{sub_mode}", Please use "{hai.__appname__} -h" to see help.')
        print(info)

    def _deal_with_download(self, *args, **kwargs):
        """
        mode = download
        下载算法、数据集、预训练模型等
        """
        opt = self.opt
        name = opt.sub_mode
        assert name, f'Download name need to be specified'

        # 匹配
        dict_info = self.uaii.list_remote_models()
        model_names = dm.misc.flatten_list([x for x in dict_info.values()])
        # model_names = [x.lower() for x in model_names]
        if name in model_names:
            self.uaii.download_model(name)
        # elif xxxx
        else:
            raise NotImplementedError(f'No resource "{name}" found.')
        