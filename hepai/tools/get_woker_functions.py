from hepai import HRModel
import asyncio, os  
from functools import wraps
from inspect import Parameter, Signature
from typing import (
    Any, 
    Callable, 
    Dict, 
    List, 
    Optional, 
    Tuple, 
    Type, 
    Union,
    AsyncGenerator,
    Generator,
    )


def _build_sync_func(func_name: str, func_doc: str, func_sig: List[Dict], return_type_str: str, model: HRModel):
    # 转换 func_sig 到 Signature 对象
    parameters = []
    for param in func_sig:
        param_name = param["name"]
        param_type = eval(param["type"]) if param["type"] != "Any" else Any
        param_default = param["default"] if param["default"] is not None else Parameter.empty

        parameters.append(
            Parameter(
                name=param_name,
                kind=Parameter.KEYWORD_ONLY,
                default=param_default,
                annotation=param_type
            )
        )

    signature_obj = Signature(parameters=parameters, return_annotation=eval(return_type_str) if return_type_str != "Any" else Any)

    # 构造异步函数
    def function_template(**kwargs):
        remote_func = getattr(model, func_name)
        result = remote_func(**kwargs)
        return result

    @wraps(function_template)
    def wrapper_func(**kwargs):
        return function_template(**kwargs)

    wrapper_func.__signature__ = signature_obj
    wrapper_func.__name__ = func_name
    wrapper_func.__doc__ = func_doc
    wrapper_func.__annotations__ = {p.name: p.annotation for p in parameters}
    wrapper_func.__annotations__["return"] = eval(return_type_str) if return_type_str != "Any" else Any

    return wrapper_func

def get_worker_sync_functions(
        name: str, 
        api_key: str = None, 
        base_url: str = None,
        print_func_info: bool = False
        ) -> List[Callable]:

    model = HRModel.connect(
        name=name,
        api_key=api_key or os.environ.get("HEPAI_API_KEY"),
        base_url=base_url or "https://aiapi.ihep.ac.cn/apiv2"
    )

    funcs_decs: list[dict[str, str]] = model.get_register_functions() # Get all remote callable functions.
    
    # 通过funcs中函数的"__name__"，"__doc__"，"__signature__"，"__return__"属性构造可调函数
    funcs: List[Callable] = []
    for func_dec in funcs_decs:
        func_name = func_dec["__name__"]
        func_doc = func_dec["__doc__"]
        func_sig = func_dec["__signature__"]
        return_type_str = func_dec["__return__"]

        async_func = _build_sync_func(func_name, func_doc, func_sig, return_type_str, model)
        funcs.append(async_func)
    if print_func_info:
        print("+"*40 + "\n")
        for func in funcs:
            print(f"函数名：{func.__name__}\n")
            print(f"函数描述：\n{func.__doc__}\n")
            print(f"函数签名：\n{func.__signature__}\n")
            print("+"*40 + "\n")
    return funcs

def _build__async_func(func_name: str, func_doc: str, func_sig: List[Dict], return_type_str: str, model: HRModel):
    # 转换 func_sig 到 Signature 对象
    parameters = []
    for param in func_sig:
        param_name = param["name"]
        param_type = eval(param["type"]) if param["type"] != "Any" else Any
        param_default = param["default"] if param["default"] is not None else Parameter.empty

        parameters.append(
            Parameter(
                name=param_name,
                kind=Parameter.KEYWORD_ONLY,
                default=param_default,
                annotation=param_type
            )
        )

    signature_obj = Signature(parameters=parameters, return_annotation=eval(return_type_str) if return_type_str != "Any" else Any)

    # 构造异步函数
    async def function_template(**kwargs):
        remote_func = getattr(model, func_name)
        result = await remote_func(**kwargs)
        return result

    @wraps(function_template)
    async def wrapper_func(**kwargs):
        return await function_template(**kwargs)

    wrapper_func.__signature__ = signature_obj
    wrapper_func.__name__ = func_name
    wrapper_func.__doc__ = func_doc
    wrapper_func.__annotations__ = {p.name: p.annotation for p in parameters}
    wrapper_func.__annotations__["return"] = eval(return_type_str) if return_type_str != "Any" else Any

    return wrapper_func

async def get_worker_async_functions(
        name: str, 
        api_key: str = None, 
        base_url: str = None,
        print_func_info: bool = False
        ) -> List[Callable]:

    model = await HRModel.async_connect(
        name=name,
        api_key=api_key or os.environ.get("HEPAI_API_KEY"),
        base_url=base_url or "https://aiapi.ihep.ac.cn/apiv2"
    )

    funcs_decs: list[dict[str, str]] = await model.get_register_functions() # Get all remote callable functions.
    
    # 通过funcs中函数的"__name__"，"__doc__"，"__signature__"，"__return__"属性构造可调函数
    funcs: List[Callable] = []
    for func_dec in funcs_decs:
        func_name = func_dec["__name__"]
        func_doc = func_dec["__doc__"]
        func_sig = func_dec["__signature__"]
        return_type_str = func_dec["__return__"]

        async_func = _build__async_func(func_name, func_doc, func_sig, return_type_str, model)
        funcs.append(async_func)
    if print_func_info:
        print("+"*40 + "\n")
        for func in funcs:
            print(f"函数名：{func.__name__}\n")
            print(f"函数描述：\n{func.__doc__}\n")
            print(f"函数签名：\n{func.__signature__}\n")
            print("+"*40 + "\n")
    return funcs
