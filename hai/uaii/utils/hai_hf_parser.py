# try:
from .hf_argparser import HfArgumentParser
# except:
    # from hf_argparser import HfArgumentParser
    
def parse_args(dataclasses_types,
        args=None,
        return_remaining_strings=False,
        look_for_args_file=True,
        args_filename=None,
        args_file_flag=None,):
    """
    Parse command-line args into instances of the specified dataclass types.

    This relies on argparse's `ArgumentParser.parse_known_args`. See the doc at:
    docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.parse_args

    Usage::
        python xx.py --arg1 val1 --arg2 val2 

    Args:
        dataclass_types:
            Dataclass type, or list of dataclass types for which we will "fill" instances with the parsed args.
        args:
            List of strings to parse. The default is taken from sys.argv. (same as argparse.ArgumentParser)
        return_remaining_strings:
            If true, also return a list of remaining argument strings.
        look_for_args_file:
            If true, will look for a ".args" file with the same base name as the entry point script for this
            process, and will append its potential content to the command line args.
        args_filename:
            If not None, will uses this file instead of the ".args" file specified in the previous argument.
        args_file_flag:
            If not None, will look for a file in the command-line args specified with this flag. The flag can be
            specified multiple times and precedence is determined by the order (last one wins).

    Returns:
        Tuple consisting of:

            - the dataclass instances in the same order as they were passed to the initializer.abspath
            - if applicable, an additional namespace for more (non-dataclass backed) arguments added to the parser
                after initialization.
            - The potential list of remaining argument strings. (same as argparse.ArgumentParser.parse_known_args)
    """
    return parse_args_into_dataclasses(
        dataclasses_types,
        args=args,
        return_remaining_strings=return_remaining_strings,
        look_for_args_file=look_for_args_file,
        args_filename=args_filename,
        args_file_flag=args_file_flag,
    )
    

def parse_args_into_dataclasses(
        dataclasses_types,
        args=None,
        return_remaining_strings=False,
        look_for_args_file=True,
        args_filename=None,
        args_file_flag=None,):
    """
    Parse command-line args into instances of the specified dataclass types.

    This relies on argparse's `ArgumentParser.parse_known_args`. See the doc at:
    docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.parse_args

    Usage::
        python xx.py --arg1 val1 --arg2 val2 

    Args:
        dataclass_types:
            Dataclass type, or list of dataclass types for which we will "fill" instances with the parsed args.
        args:
            List of strings to parse. The default is taken from sys.argv. (same as argparse.ArgumentParser)
        return_remaining_strings:
            If true, also return a list of remaining argument strings.
        look_for_args_file:
            If true, will look for a ".args" file with the same base name as the entry point script for this
            process, and will append its potential content to the command line args.
        args_filename:
            If not None, will uses this file instead of the ".args" file specified in the previous argument.
        args_file_flag:
            If not None, will look for a file in the command-line args specified with this flag. The flag can be
            specified multiple times and precedence is determined by the order (last one wins).

    Returns:
        Tuple consisting of:

            - the dataclass instances in the same order as they were passed to the initializer.abspath
            - if applicable, an additional namespace for more (non-dataclass backed) arguments added to the parser
                after initialization.
            - The potential list of remaining argument strings. (same as argparse.ArgumentParser.parse_known_args)
    """
    # assert isinstance(dataclasses_types, tuple), f'input dataclasses must be tuple, but got {type(dataclasses_types)}'
    is_tuple = isinstance(dataclasses_types, tuple)
    if not is_tuple:
        dataclasses_types = (dataclasses_types, )
    result = HfArgumentParser(dataclasses_types).parse_args_into_dataclasses(
        args=args,
        return_remaining_strings=return_remaining_strings,
        look_for_args_file=look_for_args_file,
        args_filename=args_filename,
        args_file_flag=args_file_flag,
    )
    if is_tuple:
        return result
    else:
        r1, = result
        return r1


def test():
        
    import dataclasses
    @dataclasses.dataclass
    class TestArgs:
        name: str = 'zhangsan'
        age: int = 18

    @dataclasses.dataclass
    class TestArgs2:
        name2: str = 'lisi'

    args = parse_args_into_dataclasses(TestArgs)
    print(args)
    print(args.name)

    args1, args2 = parse_args_into_dataclasses((TestArgs, TestArgs2))
    print(args1)
    print(args2)
    print(args2.name2)


if __name__ == '__main__':
    test()


