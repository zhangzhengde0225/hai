# -*- coding: utf-8 -*-

from importlib.metadata import version
__version__ = version("gwaihir")


def get_git_version():
    """
    Get the full version name with git hash, e.g. "2020.1-65-g958b7254-dirty"
    Only works if the current directory is part of the git repository.
    :return: the version name
    """
    from subprocess import Popen, PIPE
    try:
        p = Popen(['git', 'describe', '--tags', '--dirty', '--always'],
                  stdout=PIPE, stderr=PIPE)
        return p.stdout.readlines()[0].strip().decode("UTF-8")
    except:
        # in distributed & installed versions this is replaced by a string
        __git_version_static__ = "git_version_placeholder"
        if "placeholder" in __git_version_static__:
            return __version__
        return __git_version_static__
