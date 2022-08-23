import os, sys


def get_registed_module_info(registry, module=None, **kwargs):
    """
    ID', 'TYPE', 'NAME', 'STATUS', 'TAG', 'INCLUDE', 'DESCRIPTION'
    分析已注册注册模块的信息，模块的状态存在自己里。
    :param modules: 对象，Registry里的modules_dict
    :param start_id: int，从第start_id个统计模块数目。
    :return: list, (n, 4) n个模块，4: 模块ID, 模块名(内部名)，模块状态，模块描述
    """
    include_dict = kwargs.get('include_dict', None)

    if module is None:
        items = registry.module_dict.items()
        ids = registry.module_ids
    else:
        modules = [module] if isinstance(module, str) else module
        items = dict()
        ids = list()
        for i, (name, module) in enumerate(registry.module_dict.items()):
            if name in modules:
                items[name] = module
                ids.append(registry.module_ids[i])
    meta = []
    for i, (name, module) in enumerate(items):
        # name是注册模块的name
        id = ids[i]
        type = registry.name
        mname = module.name  # 模块内部的name
        mname = name if mname.lower() == 'default_name' else mname  # 如果是默认名字，用注册名替代
        mstatus = module.status  # 状态
        mdescription = module.description  # 描述
        # print(type)
        mtag = module.tag if type == 'module' else '-'  # 标签
        # mtag = module.tag
        # print(f'name: {name}')
        # print(f'module: {module.name}')
        meta.append([id, type, mname, mstatus, mtag, '-', mdescription])

    return meta
