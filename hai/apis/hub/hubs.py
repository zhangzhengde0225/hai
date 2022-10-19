
from .. import uaii


def list(**kwargs):
    """
    list all algorithms
    :return: list of algorithms
    """
    info = uaii.ps(**kwargs)
    # print(info)
    return info

def list_weights(name=None, *args, **kwargs):
    """
    list weights of algorithm by name
    :param name: algorithm name
    :return: list of weights
    """
    info = uaii.list_weights(model_name=name, *args, **kwargs)
    return info


def load(name, *args, **kwargs):
    """
    load algorithm by name  
    :param name: algorithm name 
    :return: model
    """
    model = uaii.load_model(name, *args, **kwargs)
    return model
    
def docs(name):
    """
    get algorithm docs by name
    :param name: algorithm name
    :return: docs
    """
    info = f'https://ai.ihep.ac.cn/docs/{name}'
    return info


