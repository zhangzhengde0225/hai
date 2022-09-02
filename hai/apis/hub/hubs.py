
from .. import uaii


def list():
    """
    list all algorithms
    :return: list of algorithms
    """
    info = uaii.ps()
    # print(info)
    return info


def load(name, *args, **kwargs):
    """
    load algorithm by name  
    :param name: algorithm name 
    :return: model
    """
    model = uaii.get_module(name, *args, **kwargs)
    model = model()
    return model
    
def docs(name):
    """
    get algorithm docs by name
    :param name: algorithm name
    :return: docs
    """
    info = f'https://ai.ihep.ac.cn/docs/{name}'
    return info
