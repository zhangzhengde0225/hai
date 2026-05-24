import os, sys, signal
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Union, Generator, Callable, Literal, AsyncGenerator
import threading
import atexit
import warnings
import time, asyncio
import traceback, inspect
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
import requests
import logging
from logging import Logger


from ._related_class import (
    WorkerNetworkInfo, ModelResourceInfo, WorkerStatusInfo, WorkerInfo,
    HRemoteModel
)

work_dir = os.getcwd()

# from .utils import get_uuid
from . import utils

@dataclass
class HWorkerConfig:  # (2) worker的参数配置和启动代码
    # config_file: Optional[str] = field(default=f"{work_dir}/worker_config.json", metadata={"help": "Path to the model configuration file, if None, load all models from the API"})
    # config for worker server
    host: str = field(default="127.0.0.1", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: Union[int, str, None] = field(default=42600, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})
    
    # config for controller connection
    no_register: bool = field(default=True, metadata={"help": "Do not register to controller"})
    controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    controller_prefix: str = field(default="/apiv2", metadata={"help": "Controller's route prefix"})
    
    # config for model
    speed: int = field(default=1, metadata={"help": "Model's speed"})
    limit_model_concurrency: int = field(default=100, metadata={"help": "Limit the model's concurrency"})
    stream_interval: float = field(default=0., metadata={"help": "Extra interval for stream response"})
    # permissions: dict = field(default_factory=lambda: {'groups': ['payg']}, metadata={"help": "Model's permissions, e.g., {'groups': ['default'], 'users': ['a', 'b'], 'owner': 'c'}"})
    permissions: Optional[dict] = field(default=None, metadata={"help": "Model's permissions, e.g., {'groups': ['default'], 'users': ['a', 'b'], 'owner': 'c'}"})
    description: str = field(default='This is a demo worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    author: str = field(default="hepai", metadata={"help": "Model's author"})
    debug: bool = field(default=False, metadata={"help": "Debug mode"})
    type: Literal["llm", "actuator", "preceptor", "memory", "common"] = field(default="common", metadata={"help": "Specify worker type, could be help in some cases"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    is_free: bool = field(default=True, metadata={"help": "Whether the model is free to use, if False, model owner should setup model pricing via controller"})
    _metadata: dict = field(default_factory=dict, metadata={"help": "Additional metadata for worker/model"})
    
    # config for common features
    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker, ensure the security, if enabled, the `api_key` must be provided when someone wants to access the worker's APIs"})
    enable_llm_router: bool = field(default=False, metadata={"help": "Enable LLM router, only for llm worker"})
    model_config_dir: Optional[str] = field(default=None, metadata={"help": "Directory to store model_config.yaml, if None, will try to use worker script directory or current working directory"})
    # enable_mcp: bool = field(default=False, metadata={"help": "Enable MCP (Model Context Protocol) for LLM worker"})
    owner_key: str = field(default="os.environ/HEPAI_API_KEY", metadata={"help": "Owner's API key for authenticating with controller, read from HEPAI_API_KEY env var by default"})
    
    def __post_init__(self):
        if isinstance(self.port, str):
            if self.port.lower() == 'none':
                self.port = None
            else:
                try:
                    self.port = int(self.port)
                except ValueError:
                    self.port = None
        if isinstance(self.permissions, str):
            try:
                perms = dict()
                for a in self.permissions.split(';'):
                    if ':' not in a:
                        raise ValueError(f"Invalid permissions format: '{a}'")
                    user_or_group, names = map(str.strip, a.split(':', 1))
                    if user_or_group not in ['owner', 'users', 'groups']:
                        raise ValueError(f"Invalid key in permissions: '{user_or_group}'")
                    perms[user_or_group] = (
                        [name.strip() for name in names.split(',')] if ',' in names else [names.strip()]
                    )
                # 确保owner是单个字符串
                if 'owner' in perms:
                    if isinstance(perms['owner'], list):
                        if len(perms['owner']) > 1:
                            raise ValueError(f"Only one owner is allowed, but got {perms['owner']}")
                        perms['owner'] = perms['owner'][0]
                self.permissions = perms
            except Exception as e:
                raise ValueError(f"Failed to parse permissions string: {self.permissions}. Error: {e}")

        # 解析 "os.environ/VAR_NAME" 格式的字段，从环境变量中读取实际值
        self.owner_key = self._resolve_env_var(self.owner_key, "owner_key")

    @staticmethod
    def _resolve_env_var(value: str, field_name: str) -> str:
        """解析 'os.environ/VAR_NAME' 格式的字符串，从环境变量中读取实际值"""
        if not isinstance(value, str) or not value.startswith("os.environ/"):
            return value
        env_var_name = value[len("os.environ/"):]
        env_value = os.environ.get(env_var_name)
        if env_value is None:
            warnings.warn(
                f"[HWorkerConfig] Field '{field_name}' references environment variable "
                f"'{env_var_name}', but it is not set. Value will be empty."
            )
            return ""
        return env_value


    
    def ensure_worker_config(self):
        """"""
        
    def update_from_dict(self, d: Dict):
        """更新配置"""
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)
        unknown_keys = set(d.keys()) - set(self.__dict__.keys())
        if unknown_keys:
            warnings.warn(f"[HWorkerConfig] Encountered unknown keys when updating from dict: {unknown_keys}")
        return self
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict):
        """从字典创建配置实例"""
        return cls().update_from_dict(d)


class CommonWorker:
    """
    Common Worker，用来实际处理各种函数
    v2.1支持单worker搭载多模型
    """
    def __init__(self,
                 app: FastAPI,  # FastAPI app
                 models: HRemoteModel | List[HRemoteModel],  # 模型，v2.1支持
                 worker_config: "HWorkerConfig",  # worker的配置
                 logger: Optional[Logger] = None,  # logger
                 **kwargs
                 ):
        # 配置
        self.config: HWorkerConfig = worker_config
        self.config_dict: Dict = self._init_config_dict(worker_config, **kwargs)
        self.name = self.config_dict.get("name", self.__class__.__name__)
        # 网络信息相关项目，多模型共用一个
        self.network_info: WorkerNetworkInfo = self.get_network_info()
        
        # 模型资源信息相关
        self.worker_permissions: Dict = self._parse_permissions(self.config.permissions)  # 将str转换为dict

        # 状态信息相关
        self.app = app  # "HWorkerAPP" 
        self.speed = self.config_dict.get("speed", 1)  # 这是worker的
        self.status = "idle"
        self.start_time = time.time()

        # 初始化信息
        self.models: List[HRemoteModel] = self._check_models(models)
        self._model_names = [m.name for m in self.models]
        unique_model_names = set(self._model_names)
        if len(unique_model_names) != len(self._model_names):
            raise ValueError(f"Model names should be unique, but got {self._model_names}")
        
        worker_id = self.config_dict.get("worker_id", None)
        indicators = ["worker"] + self._model_names
        self.worker_id = worker_id if worker_id else utils.gen_one_id(
            lenth=15, prefix="wk-", extra_indicators=indicators
        )
        self.stream_interval = self.config_dict.get("stream_interval", 0)
        self.owner_key = self.config_dict.get("owner_key", "")
        # self.model = model or HRemoteModel()  # deprecated, v2.1支持多模型
        
        # 建立快速查找的模型映射
        self._model_map: Dict[str, HRemoteModel] = {m.name: m for m in self.models}

        # 模型启用/禁用状态（内存缓存，由 cfg_mgr 持久化到 JSON）
        self._enabled_models: Dict[str, bool] = {m.name: True for m in self.models}

        # flag
        self._is_deleted_in_controller = False  # a flag to indicate whether the worker is deleted in controller
        # 日志
        self.logger = logger
        if self.logger:
            try:
                from hepai.tools.logger import Logger
                self.logger = Logger.get_logger("CommonWorker")
            except Exception as e:
                self.logger = logging.getLogger("CommonWorker")

        # 注册模型
        if not self.config.no_register:
            success: bool = self.register_to_controller()
            if success:  # sent hartbeat every 60s
                # 使用异步心跳以提高性能
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 在异步环境下，创建后台任务
                        loop.create_task(self.worker_heartbeat_async())
                    else:
                        # 没有事件循环，回退到线程模式
                        self.heartbeat_thread = threading.Thread(
                            target=self.worker_heartbeat, 
                            daemon=True,
                            )
                        self.heartbeat_thread.start()
                except RuntimeError:
                    # 没有事件循环，回退到线程模式
                    self.heartbeat_thread = threading.Thread(
                        target=self.worker_heartbeat, 
                        daemon=True,
                        )
                    self.heartbeat_thread.start()
            else:  # if not success, flags as local worker only
                self._is_deleted_in_controller = True

        # 标识是否已经在controller中删除，如果已经删除，则exit_handler不再向controller发送删除信息
        # 用于适配controllre端主动向worker发送删除worker时
        atexit.register(self.exit_handler)

        
        self.status = "ready"

    @property
    def base_url(self):
        """The base url of controller"""
        controller_addr = self.config.controller_address
        controller_prefix = self.config.controller_prefix
        if controller_prefix:
            return f'{controller_addr}{controller_prefix}'
        return controller_addr
    
    @property
    def worker_name(self):
        """deprecated in v2.1 for multi-model"""
        raise DeprecationWarning("This property is deprecated in v2.1 for multi-model, please use `worker_id` instead.")
        # return self.model.name or self.model.__class__.__name__
        
    @property
    def model_names(self) -> List[str]:
        if not self._model_names:
            self._model_names = [m.name for m in self.models]
        return self._model_names
    
    def _check_models(self, models: List[HRemoteModel] | HRemoteModel) -> List[HRemoteModel]:
        """检查模型是否符合要求"""
        # v2.1支持多模型
        if isinstance(models, HRemoteModel):
            models = [models]
        # 检查类型
        for model in models:  # 是HRemoteModel的实例或者子类
            if isinstance(model, HRemoteModel):
                continue
            elif issubclass(model, HRemoteModel):
                continue
            else:
                raise ValueError(f"The Model should be HRemoteModel or subclass of HRemoteModel, i.e. from hepai import HRemoteModel, but got {type(model)}")
        # 检查模型不重名
        model_names = [m.name for m in models]
        if len(model_names) != len(set(model_names)):
            raise ValueError(f"Model names should be unique, but got {model_names}")
        return models
    
    def _parse_permissions(self, permissions: Optional[Union[str, Dict]]) -> Dict:
        """worker授予用户或者组的权限"""
        if permissions is None:
            return {}
        elif isinstance(permissions, dict):
            return permissions
        elif isinstance(permissions, str):
            """user: <user1>; user: <user2>; group: <group1>, ..."""
            perms = dict()
            for a in permissions.split(';'):
                user_or_group, names = map(str.strip, a.split(':', 1))
                assert user_or_group in ['owner', 'users', 'groups'], f"Invalid key: {user_or_group}"
                values = [name.strip() for name in names.split(',')] if ',' in names else [names.strip()]
                values = [v for v in values if v]  # 去掉空字符串
                perms[user_or_group] = (values)
            # 确保owner是单个字符串
            if 'owner' in perms:
                if isinstance(perms['owner'], list):
                    if len(perms['owner']) > 1:
                        raise ValueError(f"Only one owner is allowed, but got {perms['owner']}")
                    perms['owner'] = perms['owner'][0]
        else:
            raise ValueError(f"permissions should be str or dict, but got {type(permissions)}")
        return perms
    
    def _init_config_dict(self, config: HWorkerConfig, **kwargs):
        config_dict = config.__dict__
        for k, v in kwargs.items():
            if k in config_dict:
                raise ValueError(f"Duplicate key: {k}, Please check the config class and the kwargs.")
            config_dict[k] = v
        return config_dict
    
    async def worker_heartbeat_async(self):
        """异步心跳函数，避免阻塞"""
        heartbeat_interval = self.config_dict.get("heartbeat_interval", 60)
        while True:
            await asyncio.sleep(heartbeat_interval)
            # 使用线程池执行同步的注册操作
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, self.register_to_controller, True)
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
    
    def worker_heartbeat(self):
        """间隔发送心跳的函数 - 保留用于向后兼容"""
        heartbeat_interval = self.config_dict.get("heartbeat_interval", 60)
        while True:
            time.sleep(heartbeat_interval)
            self.register_to_controller(heartbeat_flag=True)
    
    def get_network_info(self) -> WorkerNetworkInfo:
        host = self.config.host
        from .utils import auto_port, auto_worker_address, get_hostname
        port = auto_port(port=self.config.port, start=self.config.auto_start_port)
        worker_address = auto_worker_address(worker_address="auto", host=host, port=port)
        route_prefix = self.config.route_prefix
        if route_prefix:
            worker_address = f"{worker_address}{route_prefix}"
        return WorkerNetworkInfo(
            host=self.config.host,
            port=port,
            host_name=get_hostname(),
            route_prefix=route_prefix,
            worker_address=worker_address,
        )
    
    def is_model_enabled(self, model_name: str) -> bool:
        return self._enabled_models.get(model_name, True)

    def set_model_enabled(self, model_name: str, enabled: bool) -> None:
        self._enabled_models[model_name] = enabled

    def get_model_resource_info(self) -> List[ModelResourceInfo]:
        """
        v2.1 支持多模型
        v2.2 过滤禁用的模型（用于心跳上报）
        """

        model_resources = []
        for model in self.models:
            # 跳过禁用的模型
            if not self.is_model_enabled(model.name):
                continue

            model_name = model.name or model.__class__.__name__
            permission = model.permission
            if not permission:  # 如果没有设置权限，则使用worker的权限
                permission = self.worker_permissions
            owner = permission.get("owner", None)
            owner = owner if owner else self.config.author

            mr = ModelResourceInfo(
                model_name=model_name,
                model_type=self.config_dict.get("model_type", "common"),
                model_version=self.config_dict.get("model_version", "1.0"),
                model_description=self.config.description,
                model_author=self.config.author,
                model_owner=permission.get("owner", None),
                model_users=permission.get("users", []),
                model_groups=permission.get("groups", []),
                model_functions=model.all_remote_callables,
                id=model.model_id,
                created=model.created,
                owned_by=owner,
            )
            model_resources.append(mr)
        return model_resources
    
    def get_callable_functions(self, cls):
        """获取一个类的所有可调用函数"""
        callable_funcs = []
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Check if method belongs to the class and is not inherited
            if method.__qualname__.startswith(cls.__name__ + '.'):
                callable_funcs.append(name)
        return callable_funcs
    
    def get_all_callable_functions(self, cls: HRemoteModel):
        """获取一个类的所有可调用函数，包括父类的"""
        # Recursive function to collect callable methods from the class and its parent classes
        methods = {}
        # Traverse the method resolution order (MRO), which includes the class and its bases
        for subclass in inspect.getmro(cls.__class__):
            for name, method in inspect.getmembers(subclass, inspect.isfunction):
                methods[name] = method
        callable_funcs = list(methods.keys())

        # 再判断这些函数是不是可以远程调用的
        callable_funcs = [f for f in callable_funcs if hasattr(methods[f], "is_remote_callable")]

        return callable_funcs


    def get_status_info(self) -> WorkerStatusInfo:
        return WorkerStatusInfo(
            speed=self.speed,
            queue_length=self.app.get_queue_length(),
            status=self.status,
            start_time=self.start_time,
        )
    
    def get_model_by_name(self, model_name: str) -> Optional[HRemoteModel]:
        """快速获取模型对象"""
        return self._model_map.get(model_name)
    
    async def shutdown_worker(self) -> None:
        await asyncio.sleep(1)
        os.kill(os.getpid(), signal.SIGINT)
    
    def get_worker_info(self) -> WorkerInfo:
        """
        Dynamically get worker info
        """
        status_info = self.get_status_info()
        
        metadata = {
            "description": self.config.description,
            "author": self.config.author,
            "limit_model_concurrency": self.config.limit_model_concurrency,
            "permissions": self.worker_permissions,
            "uptime": time.time() - (status_info.start_time if status_info.start_time else time.time()),
            "is_free": self.config.is_free,
            "worker_name": self.config_dict.get("worker_name", None),
        }
        worker_meta = self.config._metadata
        metadata.update(worker_meta)
        
        worker_info = WorkerInfo(
            id=self.worker_id,
            type=self.config.type,
            network_info=self.network_info,
            resource_info=self.get_model_resource_info(),
            status_info=status_info,
            check_heartbeat=True,
            version=self.config_dict.get("version", "2.0"),
            metadata=metadata,
        )
        return worker_info
    
    def set_worker_pressions(self, permissions: Dict):
        """设置模型的权限, 用于动态更新，仅限于owner和admin"""
        self.worker_permissions = permissions

    def set_worker_speed(self, speed: int):
        """设置模型的速度, 用于动态更新，仅限于owner和admin"""
        self.speed = speed
    
    ### --- 此处开始是向controller发送请求的相关函数 --- ###
    @property
    def headers(self) -> dict:
        headers = {
            'Authorization': f'Bearer {self.owner_key}' if self.owner_key else '',
            'Content-Type': 'application/json'
        }
        return headers
    
    def register_to_controller(self, heartbeat_flag: bool = False):
        """
        注册和心跳
        heartbeat_flag: 用于区分是首次注册还是心跳
        """
        # logger.info(f'Register model "{self.model_name}" to controller.')

        # url = self.base_url + '/register_worker'
        url = self.base_url + '/worker/register_worker'

        if not heartbeat_flag:  # 首次注册时才检查controller的连通性，心跳时不检查以避免性能问题
            if not utils.check_controller_connectivity(self.base_url):
                msg = f"Controller unreachable at `{self.base_url}`. Please ensure the controller is running, or run this worker in standalone mode by setting `--no_register True`."
                self.logger.error(msg)
                if not self.config.no_register:
                    raise ConnectionError(msg)
                return False

        worker_info: WorkerInfo = self.get_worker_info()
        data = worker_info.to_dict()

        # 上报 worker 自身的 secret_key 给 controller, 用于 controller 反向代理鉴权
        # (controller 端的 WorkerInfoItem 显式声明了该字段, 旧版 controller 会忽略)
        worker_secret_key = getattr(self.app, "worker_secret_key", None)
        if worker_secret_key:
            data["secret_key"] = worker_secret_key

        try:
            r = requests.post(url, json=data, headers=self.headers)
            if r.status_code != 200:
                raise ValueError(f"Register worker failed. \nRequest url: {url}  Status: {r.status_code}, \nResponse: {r.text}")
        except requests.ConnectionError as e:
            error_reason = f"Cannot connect to controller at `{self.base_url}`. Is the controller running? Error: {e}"
            if heartbeat_flag:
                self.logger.error(f"Heartbeat failed (connection error), url: {url}, worker_id: {self.worker_id}")
            else:
                self.logger.error(f"Register worker to controller failed: {error_reason}")
                if not self.config.no_register:
                    raise ValueError(error_reason)
                return False
        except requests.Timeout as e:
            error_reason = f"Cannot connect to controller at `{self.base_url}`. Is the controller running? Error: {e}"
            if heartbeat_flag:
                self.logger.error(f"Heartbeat failed (timeout), url: {url}, worker_id: {self.worker_id}")
            else:
                self.logger.error(f"Register worker to controller failed: {error_reason}")
                if not self.config.no_register:
                    raise ValueError(error_reason)
                return False
        except Exception as e:
            error_reason = f"{e.__class__.__name__}: {e}"
            if heartbeat_flag:
                self.logger.error(f"Heartbeat failed, url: {url}, worker_id: {self.worker_id}. Reason: {error_reason}")
            else:
                self.logger.error(f"Register worker to controller failed. Reason: {error_reason}")
                if not self.config.no_register:
                    raise ValueError(f'Register worker to controller failed. Error: {e}')
                return False
        if heartbeat_flag:
            if self.config.debug:
                self.logger.info(f"Heartbeat sent successfully: `{worker_info.id}`")
        else:
            self.logger.info(f"Worker `{worker_info.id}` register to `{self.base_url}` successfully.")
        return True
  
    def exit_handler(self):
        """
        退出时向Contoller发送退出信息。
        三层去重：
          1) 进程内置位 `_is_deleted_in_controller`，避免 atexit + shutdown 双路径重复；
          2) 进程间用基于 ppid（gunicorn master pid）的文件锁 + marker 互斥，
             保证同一组 gunicorn worker 只发一次 delete；
          3) 任何异常只记日志不抛出，避免 atexit 阶段异常被吞 / 多 worker 互踩。
        """
        if self.config.no_register:  # 初始化时没有注册到controller，不需要发送退出信息
            return
        if self._is_deleted_in_controller:
            return
        # 先置位，避免并发/重复触发（atexit + shutdown event 双路径）
        self._is_deleted_in_controller = True

        # ---- 进程间互斥：同一 gunicorn master 下只让一个子进程发 delete ----
        import tempfile
        try:
            import fcntl  # POSIX only；Windows 下没有，回退到不去重
            _has_fcntl = True
        except ImportError:
            _has_fcntl = False

        ppid = os.getppid()  # gunicorn 子进程的 ppid = master pid；单进程跑则为 shell pid，也唯一
        safe_wid = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(self.worker_id))
        lock_path = os.path.join(
            tempfile.gettempdir(),
            f"hepai_worker_exit_{safe_wid}_{ppid}.lock",
        )
        done_marker = lock_path + ".done"

        fd = None
        already_notified = False
        if _has_fcntl:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
                fcntl.flock(fd, fcntl.LOCK_EX)  # 阻塞独占锁
                if os.path.exists(done_marker):
                    already_notified = True
            except OSError:
                # 锁失败就回退到不去重（最多多发几次 delete，controller 端能容忍）
                if fd is not None:
                    try:
                        os.close(fd)
                    except Exception:
                        pass
                fd = None

        if already_notified:
            self.logger.info("Stop worker skipped (already notified by sibling process).")
            if fd is not None:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                except Exception:
                    pass
            return

        url = self.base_url + "/worker/stop_worker"
        try:
            worker_info: WorkerInfo = self.get_worker_info()
            wid = worker_info.id
            payload = {"worker_id": wid, "permanent": False}
            r = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=5,
            )
            if r.status_code == 200:
                self.logger.info(f"Stop worker successful. res: {r.text}")
                if fd is not None:
                    try:
                        open(done_marker, "w").close()
                    except Exception:
                        pass
            else:
                self.logger.warning(
                    f"Stop worker non-200: status={r.status_code}, body={r.text}"
                )
        except Exception as e:
            self.logger.warning(f"Stop worker request failed: {e!r}")
        finally:
            if fd is not None:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                except Exception:
                    pass

    ### --- 此处是处理Controller的请求的相关函数 --- ###
    def unified_gate(
            self, 
            model: str,
            function: str,
            args: List = None,
            kwargs: Dict = None,
            ):
        """
        统一入口, 
        v2.0更新为符合FastAPI规范，易于检测错误
        v2.1支持多模型
        """
        # assert "function" in kwargs, "function is required"
        # function = kwargs.pop("function")

        if model is None:
            if len(self.models) == 1:
                # 不指定模型，且worker只搭载一个模型时，直接使用这个模型
                req_model: HRemoteModel = self.models[0]  # requested model
            else:
                raise HTTPException(status_code=400, detail=f"Model is required, but got None, and there are {len(self.models)} models in the worker `{self.worker_id}`")  
        else:
            # 使用快速查找替代列表推导式
            req_model: HRemoteModel = self._model_map.get(model)
            if req_model is None:
                raise HTTPException(status_code=404, detail=f"Model `{model}` does not exist in the worker `{self.worker_id}`")
                
        has_function = hasattr(req_model, function)
        if not has_function:
            raise HTTPException(status_code=404, detail=f"Function `{function}` does not exist in the worker `{self.worker_id}`")
        is_callable = callable(getattr(req_model, function))
        is_remote_callable = hasattr(getattr(req_model, function), "is_remote_callable")
        if not is_callable:
            raise HTTPException(status_code=405, detail=f"Function `{function}` is not callable in the worker `{self.worker_id}`")
        if not is_remote_callable:
            raise HTTPException(status_code=405, detail=f"Function `{function}` is not remote callable in the worker `{self.worker_id}`, please add `@remote_callable` decorator to the function in worker model.")
        if has_function and is_callable and is_remote_callable:
            func: Callable = getattr(req_model, function)
            try:
                # res =  func(**kwargs)
                try:
                    res = func(*args, **kwargs)
                except:
                    # 有时候因为中间层额外引入了stream参数，而一些函数不允许接收stream参数。
                    stream = kwargs.pop("stream", False)  # 为了在客户端传输stream时，不会被kwargs接收，所以pop出来
                    res = func(*args, **kwargs)
                    
                if isinstance(res, Generator):
                    return StreamingResponse(res, media_type="application/octet-stream")
                    # return StreamingResponse(res, media_type="text/event-stream")
                return res
            except Exception as e:
                # 获取报错类型：e.__class__.__name__
                tb_str = traceback.format_exception(*sys.exc_info())
                tb_str = "".join(tb_str)
                self.logger.error(f"Error: {e}.\nTraceback: {tb_str}")
                e_class = e.__class__.__name__
                error_msg = e.__dict__.get("body", None)
                error_msg = error_msg if error_msg else f"{e_class}: {str(e)}"
                if e_class == "ModuleNotFoundError":
                    raise HTTPException(status_code=404, detail=error_msg)
                elif e_class == "NotImplementedError":
                    raise HTTPException(status_code=501, detail=error_msg)
                elif e_class == "BadRequestError":
                    raise HTTPException(status_code=400, detail=error_msg)
                elif e_class == "TypeError":
                    raise HTTPException(status_code=500, detail=error_msg)
                elif e_class == "APITimeoutError":
                    raise HTTPException(status_code=504, detail=error_msg)
                ## TODO: 其他报错类型转换为合适的报错状态码
                error_msg2 = f"{e_class}: {str(e)}"
                self.logger.error(f"一种新的错误类型：{e_class}, 错误信息：{error_msg}\n{error_msg2}")
                raise HTTPException(status_code=400, detail=f'{error_msg2}\n{error_msg2}')
        else:
            raise HTTPException(status_code=404, detail=f"Function `{function}` does not exist or is not callable in the worker `{self.worker_id}`")
        
    async def unified_gate_async(
            self, 
            model: str,
            function: str,
            args: List = None,
            kwargs: Dict = None,
            ):
        """
        统一入口, 
        v2.0更新为符合FastAPI规范，易于检测错误
        v2.1支持多模型
        """
        # assert "function" in kwargs, "function is required"
        # function = kwargs.pop("function")
        # self.logger.info(f"unified_gate_async | model: {model}")
        if model is None:
            if len(self.models) == 1:
                # 不指定模型，且worker只搭载一个模型时，直接使用这个模型
                req_model: HRemoteModel = self.models[0]  # requested model
            else:
                raise HTTPException(status_code=400, detail=f"Model is required, but got None, and there are {len(self.models)} models in the worker `{self.worker_id}`")  
        else:
            # 使用快速查找替代列表推导式
            req_model: HRemoteModel = self._model_map.get(model)
            if req_model is None:
                raise HTTPException(status_code=404, detail=f"Model `{model}` does not exist in the worker `{self.worker_id}`")
                
        has_function = hasattr(req_model, function)
        if not has_function:
            raise HTTPException(status_code=404, detail=f"Function `{function}` does not exist in the worker `{self.worker_id}`")
        is_callable = callable(getattr(req_model, function))
        is_remote_callable = hasattr(getattr(req_model, function), "is_remote_callable")
        if not is_callable:
            raise HTTPException(status_code=405, detail=f"Function `{function}` is not callable in the worker `{self.worker_id}`")
        if not is_remote_callable:
            raise HTTPException(status_code=405, detail=f"Function `{function}` is not remote callable in the worker `{self.worker_id}`, please add `@remote_callable` decorator to the function in worker model.")
        if has_function and is_callable and is_remote_callable:
            func: Callable = getattr(req_model, function)
            # 判断是否为异步函数
            is_async = asyncio.iscoroutinefunction(func)
            try:
                if is_async:
                    res = await func(*args, **kwargs)
                    # try:
                    #     res = await func(*args, **kwargs)
                    # except Exception as e:
                    #     raise RuntimeError(f"Async function raised an error, please check the function. {e}")
                    # 判断是否是异步流式响应
                    if isinstance(res, AsyncGenerator):
                        #返回异步流式响应
                        return StreamingResponse(res, media_type="application/octet-stream")
                        # return StreamingResponse(res, media_type="text/event-stream") 
                    return res  
                else:
                    # res =  func(**kwargs)
                    try:
                        res = func(*args, **kwargs)
                    except:
                        # 有时候因为中间层额外引入了stream参数，而一些函数不允许接收stream参数。
                        stream = kwargs.pop("stream", False)  # 为了在客户端传输stream时，不会被kwargs接收，所以pop出来
                        res = func(*args, **kwargs)
                        
                    if isinstance(res, Generator):
                        return StreamingResponse(res, media_type="application/octet-stream")
                        # return StreamingResponse(res, media_type="text/event-stream")
                    return res
            except Exception as e:
                # 获取报错类型：e.__class__.__name__
                tb_str = traceback.format_exception(*sys.exc_info())
                tb_str = "".join(tb_str)
                self.logger.error(f"[CommonWorker]Error: {e}.\nTraceback: {tb_str}")
                e_class = e.__class__.__name__
                error_msg = e.__dict__.get("body", None)
                error_msg = error_msg if error_msg else f"{e_class}: {str(e)}"
                if e_class == "ModuleNotFoundError":
                    raise HTTPException(status_code=404, detail=error_msg)
                elif e_class == "NotImplementedError":
                    raise HTTPException(status_code=501, detail=error_msg)
                elif e_class == "BadRequestError":
                    raise HTTPException(status_code=400, detail=error_msg)
                elif e_class == "TypeError":
                    raise HTTPException(status_code=500, detail=error_msg)
                elif e_class == "APITimeoutError":
                    raise HTTPException(status_code=504, detail=error_msg)
                ## TODO: 其他报错类型转换为合适的报错状态码
                error_msg2 = f"{e_class}: {str(e)}"
                self.logger.error(f"[CommonWorker]一种新的错误类型：{e_class}, 错误信息：{error_msg}\n{error_msg2}")
                raise HTTPException(status_code=400, detail=f'{error_msg2}\n{error_msg2}')
                # raise e
        else:
            raise HTTPException(status_code=404, detail=f"Function `{function}` does not exist or is not callable in the worker `{self.worker_id}`")

