from typing import Dict, List, Literal, Optional, Union, Generator, Callable
from dataclasses import dataclass, field
import os

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi import UploadFile, File, Form, Query, Body
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, HTMLResponse

import asyncio
from asyncio import Semaphore
import threading
from pydantic import BaseModel
from logging import Logger
import httpx
import inspect
import time
from concurrent.futures import ThreadPoolExecutor
# import markdown

from ._worker_class import HWorkerConfig, HRemoteModel, CommonWorker, ModelResourceInfo
from ._related_class import WorkerStoppedInfo, WorkerInfoRequest
from . import utils
from .singletons import authorizer

class FunctionParamsItem(BaseModel):
    args: List = []
    kwargs: Dict = {}


def get_fastapi_init_params():
    # 获取 FastAPI 的 __init__ 方法签名
    init_signature = inspect.signature(FastAPI.__init__)
    # 提取参数名（排除 'self' 和可变参数）
    params = []
    for name, param in init_signature.parameters.items():
        if name == "self":
            continue
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,  # *args
            inspect.Parameter.VAR_KEYWORD       # **kwargs
        ):
            continue
        params.append(name)
    return params

class HWorkerAPP(FastAPI):
    """
    FastAPI app for worker
    多线程运行，支持多个模型
    """

    def __init__(
            self,
            models: HRemoteModel | List[HRemoteModel], 
            worker_config: HWorkerConfig = None,  # Alias of config
            logger: Logger = None,
            **worker_overrides,
            ):
        # 获取父类的所有可能参数并传递给父类
        # 获取 FastAPI 接受的参数名
        fastapi_params = get_fastapi_init_params()
        # 筛选出有效参数
        fastapi_kwargs = {
            k: v for k, v in worker_overrides.items()
            if k in fastapi_params
        }
        # 从 worker_overrides 中删除 FastAPI 的参数
        for k in fastapi_kwargs.keys():
            worker_overrides.pop(k)
        super().__init__(**fastapi_kwargs)
        self.logger = self.get_logger(logger)
        worker_config = worker_config if worker_config is not None else HWorkerConfig()
        assert isinstance(worker_config, HWorkerConfig), f"worker_config should be an instance of HWorkerConfig"
        worker_config.update_from_dict(worker_overrides)
        
        # 用于控制模型访问的信号量 - 改为每个模型独立的信号量
        self.limit_model_concurrency = worker_config.limit_model_concurrency
        self.model_semaphores: Dict[str, Semaphore] = {}  # 每个模型独立的信号量
        self.global_counter = 0
        self._model_lookup_cache: Dict[str, int] = {}  # 模型查找缓存
        
        # 初始化线程池用于I/O密集型操作
        self._thread_pool = ThreadPoolExecutor(max_workers=100, thread_name_prefix="worker_io")
        if worker_config.enable_secret_key:
            seed = utils.get_simple_machine_seed()
            worker_secret_key = utils.gen_one_key(prefix='sk-', lenth=47, seed=seed)
            self.logger.info(f"Worker secret key: `{worker_secret_key}`, please pass it in the `Authorization` header when you call this worker.")
            authorizer.secret_key = worker_secret_key
        else:
            worker_secret_key = None
        self.worker_secret_key = worker_secret_key
        # 初始化模型信号量和缓存
        self._init_model_resources(models=models)
        self._init_routers(config=worker_config)
        
        
        self.worker = CommonWorker(
            app=self, models=models, worker_config=worker_config, 
            logger=self.logger)
        
    
        self._docs_content_cache = None  # 缓存docs内容
        self._html_mk_content_cache = None  # 缓存markdown内容
        self._cache_lock = asyncio.Lock()  # 缓存锁防止竞态条件

    def _init_model_resources(self, models: Union[HRemoteModel, List[HRemoteModel]]):
        """初始化模型资源：信号量和查找缓存"""
        if not isinstance(models, List):
            models = [models]
        for i, model in enumerate(models):
            model_name = model.name
            # 为每个模型创建独立的信号量
            self.model_semaphores[model_name] = asyncio.Semaphore(self.limit_model_concurrency)
            # 建立模型名到索引的快速查找缓存
            self._model_lookup_cache[model_name] = i
        
    
    def _init_routers(self, config: HWorkerConfig):
        
        # 1 index router
        index_router = APIRouter(prefix="", tags=["base"])
        index_router.get("/")(self.index)
        self.include_router(index_router)

        # 2 worker router
        worker_router = self.get_worker_router(router_prefix=config.route_prefix)
        self.include_router(worker_router)
        
        # 3 llm router
        if config.enable_llm_router:
            from .routers.llm_router import LLMRouterGroup
            llm_rg = LLMRouterGroup(prefix=config.route_prefix, parent_app=self)
            self.include_router(llm_rg.router, prefix=llm_rg.prefix, tags=llm_rg.tags)
        
    def get_worker_router(self, router_prefix: str = ""):
        # router_prefix = self.worker.config_dict.get("route_prefix", "/apiv2")
        router = APIRouter(prefix=router_prefix, tags=["worker"])
        router.post("/worker_unified_gate/")(self.worker_unified_gate)
        router.post("/worker_unified_gate/{function}")(self.worker_unified_gate)
        router.post("/worker_unified_gate/{model}/{function}")(self.worker_unified_gate)  # 多模型模式下，需要指定模型
        router.get("/worker_get_status")(self.worker_get_status)
        router.post("/shutdown_worker")(self.shutdown_worker)
        
        router.post("/worker/get_worker_info")(self.get_worker_info)  # 这个路由是为了与controller相同的格式，使得client也能调用
        router.post("/worker/unified_gate")(self.worker_unified_gate)  # 这个路由是为了与controller相同的格式，使得client也能调用
        router.get("/worker/models")(self.get_models)
        router.get("/worker/monitor_status")(self.get_monitor_status)  # 监控状态接口
        return router

    @classmethod
    def get_logger(cls, logger: Logger = None):
        if logger is None:
            try:
                from ...utils._logger import Logger
                logger = Logger.get_logger("worker_app.py")
            except:
                import logging
                logger = logging.getLogger("worker_app.py")
        return logger

    @property
    def host(self):
        return self.worker.network_info.host
    
    @property
    def port(self):
        return self.worker.network_info.port
    

    def get_queue_length(self, model_name: str = None):
        """获取队列长度，如果指定模型则返回该模型的队列长度，否则返回总队列长度"""
        if model_name:
            model_semaphore = self.model_semaphores.get(model_name)
            if model_semaphore is None:
                return 0
            try:
                _value = model_semaphore._value
                _num_waiters = len(model_semaphore._waiters) if hasattr(model_semaphore, "_waiters") and model_semaphore._waiters is not None else 0
                return self.limit_model_concurrency - _value + _num_waiters
            except Exception:
                return 0
        else:
            # 返回所有模型的总队列长度
            total_queue = 0
            for semaphore in self.model_semaphores.values():
                try:
                    _value = semaphore._value
                    _num_waiters = len(semaphore._waiters) if hasattr(semaphore, "_waiters") and semaphore._waiters is not None else 0
                    total_queue += self.limit_model_concurrency - _value + _num_waiters
                except Exception:
                    continue
            return total_queue
            
    def release_model_semaphore(self, model_semaphore: Semaphore):
        """释放指定模型的信号量"""
        if model_semaphore is not None:
            model_semaphore.release()
            
    async def index(self):
        # 返回监控面板HTML页面
        try:
            html_file_path = os.path.join(os.path.dirname(__file__), "html", "worker_index.html")
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        except Exception as e:
            self.logger.error(f"Failed to load HTML file: {e}")
            # 如果HTML文件加载失败，返回简单的错误页面
            error_content = f"""
            <html>
                <head>
                    <title>HepAI Worker - Error</title>
                </head>
                <body>
                    <h1>Worker Index Page Error</h1>
                    <p>无法加载监控页面: {str(e)}</p>
                    <p>Worker ID: {self.worker.worker_id}</p>
                    <p>API Documentation: <a href="/docs">/docs</a></p>
                </body>
            </html>
            """
            return HTMLResponse(content=error_content)

    async def worker_unified_gate(
            self,
            function_params: FunctionParamsItem,
            model: str = None,
            function: str = "__call__",
            ):
        self.global_counter += 1
        
        # 确定使用的模型
        if model is None:
            if len(self.worker.models) == 1:
                model = self.worker.models[0].name
            else:
                raise HTTPException(status_code=400, detail="Model parameter is required when multiple models available")
        
        # 检查模型是否存在
        if model not in self.model_semaphores:
            raise HTTPException(status_code=404, detail=f"Model '{model}' not found")
        
        # 获取该模型的信号量
        model_semaphore = self.model_semaphores[model]
        await model_semaphore.acquire()
        
        # print(f"[{self.global_counter}] Acquired semaphore for model '{model}'. Current queue length: {self.get_queue_length(model)}")
        
        try:
            rst = await self.worker.unified_gate_async(
                model=model,
                function=function, 
                args=function_params.args,
                kwargs=function_params.kwargs)
        except Exception as e:
            # await self.release_model_semaphore(model)
            # self.release_model_semaphore(model)
            self.release_model_semaphore(model_semaphore)
            raise e
        
        # background_tasks.add_task(self.release_model_semaphore, model_semaphore)
        self.release_model_semaphore(model_semaphore)
        return rst
    
    async def worker_get_status(self):
        return self.worker.get_status_info().to_dict()
    
    async def get_worker_info(
            self, 
            worker_info_request: WorkerInfoRequest,
            # user_auth: HAPIKeyAuth = api_key_auth,
            ) -> JSONResponse:
        """
        与controller的worker_info接口一致，以便client调用
        """
        # return self.worker.get_worker_info()
        rst = self.worker.get_worker_info()
        return rst

    async def get_models(self):
        mrs: List[ModelResourceInfo] = self.worker.get_model_resource_info()
        
        return {
            "object": "list",
            "data": [mr.to_dict() for mr in mrs],
        }
    
    async def get_monitor_status(self):
        """获取实时监控状态信息"""
        try:
            # 获取每个模型的并发情况
            model_status = {}
            total_queue = 0
            total_active = 0
            
            for model_name, semaphore in self.model_semaphores.items():
                try:
                    available = semaphore._value
                    waiters = len(semaphore._waiters) if hasattr(semaphore, "_waiters") and semaphore._waiters is not None else 0
                    active = self.limit_model_concurrency - available
                    queue = waiters
                    
                    model_status[model_name] = {
                        "active": active,
                        "queue": queue,
                        "available": available,
                        "limit": self.limit_model_concurrency
                    }
                    
                    total_queue += queue
                    total_active += active
                except Exception as e:
                    self.logger.warning(f"Failed to get status for model {model_name}: {e}")
                    model_status[model_name] = {
                        "active": 0,
                        "queue": 0,
                        "available": self.limit_model_concurrency,
                        "limit": self.limit_model_concurrency
                    }
            
            # 获取worker基本状态
            status_info = self.worker.get_status_info()
            
            return {
                "timestamp": time.time(),
                "total_active": total_active,
                "total_queue": total_queue,
                "total_limit": len(self.model_semaphores) * self.limit_model_concurrency,
                "model_status": model_status,
                "worker_id": self.worker.worker_id,
                # "uptime": time.time() - (status_info.start_time if status_info.start_time else time.time()),
                "model_count": len(self.worker.models),
                "global_counter": self.global_counter
            }
        except Exception as e:
            self.logger.error(f"Failed to get monitor status: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }
    
    
    async def shutdown_worker(self, background_tasks: BackgroundTasks):
        """接收来自Ctrl的关闭worker的信息"""
        background_tasks.add_task(self.worker.shutdown_worker)
        self.worker._is_deleted_in_controller = True
        wid = self.worker.worker_id
        return WorkerStoppedInfo(
            id=wid, stopped=True, 
            message=f"Worker `{wid}` shutdown",
            shutdown=True,
            )

    @classmethod
    def register_worker(
            cls,
            model: HRemoteModel = None,
            worker_config: HWorkerConfig = None,
            daemon: bool = False,
            standalone: bool = False,
            **kwargs,
            ):
        """注册HModelWorker到HaiDDF"""
        from .utils import run_standlone_worker_demo
        if standalone:  # 独立程序模式，用户测试程序
            # cls().logger.info("Running `worker` in standalone mode.")
            print("Running `worker` in standalone mode.")
            return run_standlone_worker_demo()
        
        assert model is not None, f"Model should be not None"
        import uvicorn
        app: FastAPI = HWorkerAPP(model, worker_config=worker_config, **kwargs)
        def run_uvicron():
            uvicorn.run(app, host=app.host, port=app.port)

        if daemon:  # 守护进程模式，app workre在后台运行
            t = threading.Thread(target=run_uvicron, daemon=True)
            t.start()
            return app.worker.get_worker_info()
        else:  # 正常模式，app worker在前台运行
            run_uvicron()

    def run(self):
        import uvicorn
        uvicorn.run(self, host=self.host, port=self.port)
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, '_thread_pool') and self._thread_pool:
            self._thread_pool.shutdown(wait=False)







