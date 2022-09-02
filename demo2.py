
## SDK 模块化的使用方法，与python面向对象的方法一致



class GODNet(dm.nn.AbstractModule):
    def __init__(self):
        super(GODNet, self).__init__()

        self.data_loader = dm.nn.UAII.build_stream('vis_loader')
        self.pre_process = None
        self.godnet = dm.nn.load_module('godnet')
        self.post_process = None
        self.out_exporter = dm.nn.UAII.build_stream('vis_exporter')

    def infer(self):
        rets = self.godnet.run(task='infer')
        for i, rets in enumerate(rets):
            print(f'{i}: {rets}')
        pass