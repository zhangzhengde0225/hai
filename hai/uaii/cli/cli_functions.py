

class CLIFunctions(object):

    def _deal_with_list(self, *args, **kwargs):
        """mode = list"""
        opt = self.opt
        sub_mode = opt.sub_mode
        print(self.uaii)
        print(self.uaii.ps(**kwargs))