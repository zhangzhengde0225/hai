

# import types
# from . import resources
# from ._related_class import WorkerInfo
# from typing import Union

# class LRemoteModel:
#     """
#     Local Remote Model
#     """

#     def __init__(
#             self,
#             name: str,
#             worker_info: WorkerInfo,
#             worker_resource: Union[resources.AsyncWorker, resources.Worker]
#             ) -> None:
#         self.name = name
#         self.wr: Union[resources.AsyncWorker, resources.Worker] = worker_resource
#         if not isinstance(worker_info, WorkerInfo):
#             raise ValueError(f"Failed to get remote model: {worker_info}")

#         self.model_resource = worker_info.get_model_resource(model_name=name)
#         self.model_functions = self.model_resource.model_functions
#         # self.model_functions = ["train", "__call__"]
#         if len(self.model_functions) == 0:
#             raise ValueError(f"Remote model `{self.name}` has no functions can be called remotely, please check the worker model.")

#         # 自动注册远程模型的函数
#         for func in self.model_functions:
#             original_func = self.function_warpper(self.name, func)
#             # Use functools.wraps to preserve original function metadata when creating new methods
#             # @functools.wraps(original_func)
#             # def wrapper(*args, **kwargs):
#             #     return original_func(*args, **kwargs)
#             # setattr(self, func, types.MethodType(wrapper, self))
#             setattr(self, func, types.MethodType(original_func, self))
   

#     def function_warpper(self, model_name: str, function_name: str):
#         def call_remote_function(*args, **kwargs):
#             if isinstance(args[0], LRemoteModel):
#                 # 为了处理通过types.MethodType注册时，第一个参数是self的情况
#                 args = args[1:]
#             rst =  self.wr.request(
#                 target={
#                     "model": model_name, 
#                     "function": function_name
#                     },
#                 args=args,
#                 kwargs=kwargs,
#             )
#             return rst
#         return call_remote_function
    
#     def __call__(self, *args, **kwargs):
#         return self.function_warpper(self.name, '__call__')(*args, **kwargs)

#     def functions(self):
#         return self.model_functions


# class LRModel(LRemoteModel):
#     """
#     Alias of Local Remote Model
#     """
#     ...

import os
import types
from typing import Union
from . import resources
from ._related_class import WorkerInfo

class LRemoteModel:
    """
    Local Remote Model
    """
    def __init__(
            self,
            name: str,
            worker_info: WorkerInfo,
            worker_resource: Union[resources.AsyncWorker, resources.Worker]
            ) -> None:
        
        self.name = name
        self.wr: Union[resources.AsyncWorker, resources.Worker] = worker_resource
        if not isinstance(worker_info, WorkerInfo):
            raise ValueError(f"Failed to get remote model: {worker_info}")
        self.model_resource = worker_info.get_model_resource(model_name=name)
        self.model_functions = self.model_resource.model_functions
        
        # 如果远程模型没有可调用函数，则抛出异常
        if len(self.model_functions) == 0:
            raise ValueError(f"Remote model `{self.name}` has no functions that can be called remotely. Please check the worker model.")

        # 根据资源类型（同步/异步）注册远程函数
        for func in self.model_functions:
            method = self._create_remote_method(name, func)
            setattr(self, func, types.MethodType(method, self))

        # 同样，根据资源类型为 __call__ 方法绑定同步或异步实现
        call_method = self._create_remote_method(name, '__call__')
        setattr(self, '__call__', types.MethodType(call_method, self))

    def _create_remote_method(self, model_name: str, function_name: str):
        """
        根据是同步 Worker 还是异步 AsyncWorker，创建相应的调用方法。
        """
        if isinstance(self.wr, resources.AsyncWorker):
            # 异步调用
            async def async_call_remote_function(*args, **kwargs):
                # 当通过 types.MethodType 绑定时，第一个参数是 self
                if args and isinstance(args[0], LRemoteModel):
                    args = args[1:]
                rst = await self.wr.request(
                    target={
                        "model": model_name,
                        "function": function_name
                    },
                    args=args,
                    kwargs=kwargs,
                )
                return rst
            return async_call_remote_function
        else:
            # 同步调用
            def sync_call_remote_function(*args, **kwargs):
                if args and isinstance(args[0], LRemoteModel):
                    args = args[1:]
                rst = self.wr.request(
                    target={
                        "model": model_name,
                        "function": function_name
                    },
                    args=args,
                    kwargs=kwargs,
                )
                return rst
            return sync_call_remote_function
    
    @property
    def functions(self):
        """
        获取远程模型提供的所有可调用函数名称。
        """
        return self.model_functions
    
    def connect(
        name: str,
        base_url: str = "https://aiapi.ihep.ac.cn/apiv2",
        api_key: str = os.getenv("HEPAI_API_KEY"),
        **kwargs,
    )-> "LRemoteModel":
        """
        Connect to hepai resources. such as remote model, llm, etc.
        Args:
            name (str): The name of the resource to connect to.
            base_url (str): The base URL of the resource.
        """
        from hepai import HepAI
        assert name, "Please provide the model name, you can use `client.models.list()` to get the model name."
        client = HepAI(
            base_url=base_url,
            api_key=api_key,
            **kwargs,
            )
        model: LRemoteModel = client.get_remote_model(model_name=name)
        return model


class LRModel(LRemoteModel):
    """
    Alias of Local Remote Model
    """
    ...
    
class RemoteModel(LRemoteModel):
    """
    Alias of Local Remote Model
    """
    ...