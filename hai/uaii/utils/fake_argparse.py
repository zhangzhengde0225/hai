"""
python的argparse模块不能使用两个，
例如：在大型项目中，某些子模块使用了argparse来解析参数，而主程序也使用了argparse，由于主程序引用了子程序，子程序先被加载，
此时只有子程序的argparse可用，而主程序的argparse不可用，这样就会导致主程序的argparse解析出错。
解决方案：damei库提供一个假的argparse，拥有与系统的argparse相同的函数，但是不会解析命令行参数
在子程序中:
    parser = dm.argparse.ArgumentParser() 来替代parser = argparse.ArgumentParser()

"""
from .config_loader import PyConfigLoader as Config


class Args(object):
    def __init__(self, *args, **kwargs):
        """
        properties:
            name: e.g. source
            short_name: e.g. s
            help: e.g. source help
            # default: e.g. default value
            value: e.g. value
            type: e.g. str
        """

        for arg in args:
            if arg.startswith('--'):
                self.name = arg[2:]
            elif arg.startswith('-'):
                self.short_name = arg[1:]

        # self.short_name = kwargs.get('short_name', None)
        self.nargs = kwargs.get('nargs', None)
        self._type = kwargs.get('type', None)
        self.default = kwargs.get('default', None)
        self.help = kwargs.get('help', None)
        self.action = kwargs.get('action', None)

    @property
    def type(self):
        if self.nargs is None:
            return self._type
        else:
            return list

    @property
    def value(self):
        if self.action == 'store_true':
            return False
        elif self.action == 'store_false':
            return True
        elif self.type == bool:
            return bool(self.default)
        elif self.type == int:
            if self.default is None:
                return None
            return int(self.default)
        elif self.type == float:
            return float(self.default)
        elif self.type == str:
            ret = self.default if self.default is None else str(self.default)
            return ret
        else:
            return self.default


class ArgumentParser(object):
    """TODO: 还有一些函数没完善，例如add_argument_group"""

    def __init__(self, *args, **kwargs):
        self._args = []
        self._args_dict = {}
        self.prog = kwargs.get('prog', None)
        self.description = kwargs.get('description', None)

    def __repr__(self):
        stored_args = []
        for k, v in self._args_dict.items():
            k = k.replace('-', '_')
            v2 = getattr(self, k)
            stored_args.append(f'{k}={v2}')  # 如果直接返回v，则使用opt.attr = new_value复制后，不显示新的值，改成v2，则显示新的参数
        stored_args = ', '.join(stored_args)
        format_str = f'Namespace({stored_args}) in {self.__class__}'
        return format_str

    def __dict__(self):
        return self._args_dict

    @property
    def args(self):
        return self._args

    def parse_args(self):
        name = self.prog if self.prog else 'cfg_from_argparser'
        return Config.from_argparser(self, name=name)

    def parse_known_args(self):
        return self.args, []

    def add_argument(self, *args, **kwargs):
        # print('x2x')
        arg = Args(*args, **kwargs)
        self._args.append(arg)  # object
        name = arg.name
        if '-' in name:
            name = name.replace('-', '_')
        self._args_dict[name] = arg.value

        setattr(self, name, arg.value)      
        # print(name)

    def add_argument_group(self, *args, **kwargs):
        pass

    def add_mutually_exclusive_group(self, *args, **kwargs):
        pass

    def add_subparsers(self, *args, **kwargs):
        pass

    def add_help(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exit(self, *args, **kwargs):
        pass

    def print_help(self, *args, **kwargs):
        pass

    def print_usage(self, *args, **kwargs):
        pass

    def print_version(self, *args, **kwargs):
        pass

    def set_defaults(self, *args, **kwargs):
        pass

    def set_description(self, *args, **kwargs):
        pass

    def set_epilog(self, *args, **kwargs):
        pass

    def set_usage(self, *args, **kwargs):
        pass


# def ArgumentParser(*args, **kwargs):
    # return FakeArgparse(*args, **kwargs)
