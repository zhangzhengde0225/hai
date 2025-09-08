from typing import Dict, List, Literal, Optional, Union, Generator, Callable
from dataclasses import dataclass, field

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
# import markdown

from ._worker_class import HWorkerConfig, HRemoteModel, CommonWorker, ModelResourceInfo
from ._related_class import WorkerStoppedInfo, WorkerInfoRequest, WorkerUnifiedGateRequest
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
        
        # 用于控制模型访问的信号量
        self.limit_model_concurrency = worker_config.limit_model_concurrency
        self.model_semaphore: Semaphore = asyncio.Semaphore(self.limit_model_concurrency)  # 初始化信号量
        self.global_counter = 0
        if worker_config.enable_secret_key:
            seed = utils.get_simple_machine_seed()
            worker_secret_key = utils.gen_one_key(prefix='sk-', lenth=47, seed=seed)
            self.logger.info(f"Worker secret key: `{worker_secret_key}`, please pass it in the `Authorization` header when you call this worker.")
            authorizer.secret_key = worker_secret_key
        else:
            worker_secret_key = None
        self.worker_secret_key = worker_secret_key

        self.worker = CommonWorker(
            app=self, models=models, worker_config=worker_config, 
            logger=self.logger)
        self._init_routers(config=worker_config)

        self._docs_content_cache = None  # 缓存docs内容
        self._html_mk_content_cache = None  # 缓存markdown内容

    def _init_routers(self, config: HWorkerConfig):
        
        # 1 index router
        index_router = APIRouter(prefix="", tags=["base"])
        index_router.get("/")(self.index)
        self.include_router(index_router)

        # 2 worker router
        worker_router = self.get_worker_router()
        self.include_router(worker_router)
        
        # 3 llm router
        if config.enable_llm_router:
            from .routers.llm_router import LLMRouterGroup
            llm_rg = LLMRouterGroup(prefix=config.route_prefix, parent_app=self)
            self.include_router(llm_rg.router, prefix=llm_rg.prefix, tags=llm_rg.tags)
        
    def get_worker_router(self):
        router_prefix = self.worker.config_dict.get("route_prefix", "/apiv2")
        router = APIRouter(prefix=router_prefix, tags=["worker"])
        router.post("/worker_unified_gate/")(self.worker_unified_gate)
        router.post("/worker_unified_gate/{function}")(self.worker_unified_gate)
        router.post("/worker_unified_gate/{model}/{function}")(self.worker_unified_gate)  # 多模型模式下，需要指定模型
        router.get("/worker_get_status")(self.worker_get_status)
        router.post("/shutdown_worker")(self.shutdown_worker)
        
        router.post("/worker/get_worker_info")(self.get_worker_info)  # 这个路由是为了与controller相同的格式，使得client也能调用
        router.post("/worker/unified_gate")(self.worker_unified_gate)  # 这个路由是为了与controller相同的格式，使得client也能调用
        router.get("/worker/models")(self.get_models)
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
    

    def get_queue_length(self):
        model_semaphore: asyncio.Semaphore = self.model_semaphore
        if model_semaphore is None:
            return 0
        try:
            _value = model_semaphore._value
            _num_waiters = len(model_semaphore._waiters) if hasattr(model_semaphore, "_waiters") and model_semaphore._waiters is not None else 0
            return self.limit_model_concurrency - _value + _num_waiters
        except Exception:
            return 0

    async def release_model_semaphore(self):
        if self.model_semaphore is not None:
            self.model_semaphore.release()

    async def index(self):
        worker_name = self.worker.worker_id
        fastapi_docs_url = f"http://{self.host}:{self.port}/docs"
        # 缓存docs内容，避免重复请求
        if self._docs_content_cache is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(fastapi_docs_url)
                self._docs_content_cache = response.text
        docs_content = self._docs_content_cache

        model_names = [m.name for m in self.worker.models]
        markdown_content = f"""
# HepAI Worker API
- Worker Name: **{worker_name}**
- Models: **{model_names}**
"""
        mrs = self.worker.get_model_resource_info()
        for mr in mrs:
            markdown_content += f"""
### {mr.model_name}
- Type: {mr.model_type}
- Functions: {mr.model_functions}
"""
        # 缓存markdown转换结果
        if self._html_mk_content_cache is None:
            import markdown
            self._html_mk_content_cache = markdown.markdown(markdown_content)
        html_mk_content = self._html_mk_content_cache

        content = f"""
            <html>
                <head>
                    <title>HepAI Worker Info</title>
                </head>
                <body>
                    <div style="padding-left: 20px;">
                        {html_mk_content}
                    </div>
                    <div>
                        {docs_content}
                    </div>
                </body>
            </html>
            """
        return HTMLResponse(content=content)

    async def worker_unified_gate(
            self,
            function_params: FunctionParamsItem,
            model: str = None,
            function: str = "__call__",
            ):
        self.global_counter += 1
        await self.model_semaphore.acquire()
        try:
            rst = await self.worker.unified_gate_async(
                model=model,
                function=function, 
                args=function_params.args,
                kwargs=function_params.kwargs)
        except Exception as e:
            await self.release_model_semaphore()
            raise e
        background_tasks = BackgroundTasks()
        background_tasks.add_task(self.release_model_semaphore)
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
        return self.worker.get_worker_info()

    async def get_models(self):
        mrs: List[ModelResourceInfo] = self.worker.get_model_resource_info()
        
        return {
            "object": "list",
            "data": [mr.to_dict() for mr in mrs],
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







