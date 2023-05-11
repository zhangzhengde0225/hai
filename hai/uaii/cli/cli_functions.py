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
        elif sub_mode in ['models', 'model']:  # hai list models
            from hai.apis.workers_api.model import HaiModel
            ret = HaiModel.list()
            info = dm.misc.dict2info(ret)
        elif sub_mode in ['all_workers_info', 'all_workers']:
            from hai.apis.workers_api.model import HaiModel
            info = HaiModel.all_workers_info()
            info = dm.misc.dict2info(info)
            
        else:
            raise NotImplementedError(f'Not implemented sub_mode: "{sub_mode}", Please use "{hai.__appname__} -h" to see help.')
        print(info)

    def _deal_with_download(self, *args, **kwargs):
        """
        mode = download
        下载算法、数据集、预训练模型等

        addtional_params: model(default), architecture, dataset, pretrained_model
        """
        opt = self.opt
        name = opt.sub_mode
        a_param = opt.sub_sub_mode  # additonal_parameter
        assert name, f'Download name need to be specified'
        a_param = a_param if a_param else 'model'  # default download algorithm

        if a_param == 'model':
            # 匹配
            dict_info = self.uaii.list_remote_models()
            model_names = dm.misc.flatten_list([x for x in dict_info.values()])
            # model_names = [x.lower() for x in model_names]
            if name in model_names:
                self.uaii.download_model(name)
            else:
                raise NotImplementedError(f'No resource "{name}" found. opt: {opt}')

        elif a_param.startswith('arch'):
            self.uaii.download_architecture(name)
            
        elif a_param.startswith('dataset'):
            raise NotImplementedError(f'Not implemented download dataset: "{name}"')
        else:
            raise NotImplementedError(f'Not implemented download: "{name}". opt: {opt}')

    def _deal_with_start(self, *args, **kwargs):
        """
        mode = start
        example:
            >>> hai start server <port>  # default port is 9999
        """

        parser = hai.argparse.ArgumentParser()
        parser.add_argument('--mode', type=str, default='start', help='start|stop|restart mode')
        parser.add_argument('--insecure', action='store_true', help='use secure grpc or insecure grpc')
        parser.add_argument('-p', '--port', type=int, default=9999, help='port to listen on')
        parser.add_argument('--debug', '-d', default=True, action='store_true', help='debug mode')
        args = parser.parse_args()

        opt = self.opt
        server = opt.sub_mode
        port = opt.sub_sub_mode

        args.model = 'start'
        args.insecure = kwargs.get('insecure', args.insecure)
        args.port = kwargs.get('port', args.port)
        args.port = port if port else args.port  # if specified port explicitly, use it
        args.debug = kwargs.get('debug', args.debug)

        from hai.uaii.server import run as run_server
        run_server(args)

        # print(f'opt: {opt}')
