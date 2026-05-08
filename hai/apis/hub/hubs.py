
import hai.apis as _apis


def list(**kwargs):
    """
    list all algorithms
    :return: list of algorithms
    """
    info = _apis.uaii.ps(**kwargs)
    # print(info)
    return info

def list_weights(name=None, *args, **kwargs):
    """
    list weights of algorithm by name
    :param name: algorithm name
    :return: list of weights
    """
    info = _apis.uaii.list_weights(model_name=name, *args, **kwargs)
    return info


def load(name, *args, **kwargs):
    """
    load algorithm by name
    :param name: algorithm name
    :return: model
    """
    model = _apis.uaii.load_model(name, *args, **kwargs)
    return model
    
def docs(name):
    """
    get algorithm docs by name
    :param name: algorithm name
    :return: docs
    """
    info = f'https://ai.ihep.ac.cn/docs/{name}'
    return info


