import damei as dm

class CLIFunctions(object):

    def _deal_with_list(self, *args, **kwargs):
        """mode = list"""
        opt = self.opt
        sub_mode = opt.sub_mode
        if sub_mode == 'remote':
            dict_info = self.uaii.list_remote_models()
            info = dm.misc.dict2info(dict_info)
            print(info)
            return
        print(self.uaii.ps(**kwargs))

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
        