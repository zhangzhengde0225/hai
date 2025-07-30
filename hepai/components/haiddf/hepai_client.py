"""
v2.0 基于HClient的客户端
"""
from dataclasses import dataclass, field, asdict


from .hclient import HClient, HClientConfig, AsyncHClient
from .hclient import resources

from .hclient._related_class import HRemoteModel, WorkerInfo, WorkerStatusInfo, WorkerStoppedInfo
from .hclient._remote_model import LRemoteModel



@dataclass
class HepAIClientConfig(HClientConfig):
    base_url: str = "https://aiapi001.ihep.ac.cn/apiv2"


class HepAIClient(HClient):
    """
    HepAI Client v2.0

    Usage:
        ```python
        client = HepAIClient()
        client.list_workers()
        ```
    """

    def __init__(
            self, 
            config: HClientConfig = None,
            **overrides,
            ):
        config = config or HClientConfig()
        super().__init__(config, **overrides)

        self.worker = resources.Worker(self)
        self.key = resources.Key(self)
        self.user = resources.User(self)
        self.agents = resources.Agents(self)

     ## --- 关于Worker的函数 --- ## 
    def list_workers(self):
        return self.worker.list_workers()
    
    def get_worker_info(
            self, 
            worker_id: str = None, 
            model_name: str = None,
            ) -> WorkerInfo:
        """
        Get worker info by worker_id via http request
    
        Args:
            worker_id (str): Worker ID
        """
        return self.worker.get_info(worker_id=worker_id, model_name=model_name)
    
    def get_worker_status(self, worker_id: str, refresh: bool = False) -> WorkerStatusInfo:
        """
        Get worker status by worker_id via http request
        
        Args:
            worker_id (str): Worker ID
            refresh (bool): Whether to refresh the worker status
        """
        return self.worker.get_status(worker_id=worker_id, refresh=refresh)

    def stop_worker(self, worker_id: str, permanent: bool = False) -> WorkerStoppedInfo:
        """
        Stop worker by worker_id via http request
        
        Args:
            worker_id (str): Worker ID
            permanent (bool): Whether to stop the worker permanently
        """
        return self.worker.stop(worker_id=worker_id, permanent=permanent)

    def refresh_all_workers(self) -> dict:
        """
        Refresh all workers
        """
        return self.worker.refresh_all()
    
    def get_remote_model(self, model_name: str) -> LRemoteModel:
        """
        Get a remote model
        """
        return self.worker.get_remote_model(model_name=model_name)
    
    def request_worker(
            self,
            target: dict,
            args: list = None,
            kwargs: dict = None,
            ):
        """
        Request worker via http request

        Args:
            target (dict): Target worker and function, for example: {"model": "HRemoteModel", "function": "hello_world"}
            args (list): Arguments, can by any thing you defined in your `HRemoteModel`
            kwargs (dict): Keyword arguments, can by any thing you defined in your `HRemoteModel`
        """
        return self.worker.request(target=target, args=args, kwargs=kwargs)

    def register_worker(
            self,
            model: HRemoteModel,
            daemon: bool = False,
            standalone: bool = False,
            ):
        """
        注册Worker到服务端

        Args:
            model (HRemoteModel): Worker模型
            daemon (bool): 是否以守护进程方式启动
            standalone (bool): 是否以独立进程方式启动
        """
        return self.worker.register(model, daemon=daemon, standalone=standalone)
    
    def run_demo_worker_and_register(
            self,
        ):
        return self.worker.register(standalone=True)

    
    ## # --- 关于User的函数 --- ##
    def list_users(self):
        """
        List all users
        Note: Only admin can use this function
        """
        return self.user.list_users()
    
    def create_user(self, **kwargs):
        """
        Create a new user
        Note: Only admin can use this function
        """
        return self.user.create_user(**kwargs)
    
    def delete_user(self, user_id: str):
        """
        Delete a user
        Note: Only admin can use this function
        """
        return self.user.delete_user(user_id=user_id)
    
    def auth_user(self, username: str, password: str):
        """
        Auth a user by username and password
        """
        return self.user.auth_user(username=username, password=password)
    
    ### --- 关于Key的函数 --- ###
    def list_api_keys(self):
        """
        List all keys
        Note: Only admin can use this function
        """
        return self.key.list_api_keys()
    
    def create_api_key(self, **kwargs):
        """
        Create a new key
        Note: Only admi and app admin can use this function
        Args:
            key_name (str): Key name, default is "Default"
            valid_time (int): Valid time (days), default is 30
            user_id (str): User ID, default is None, means create a key for myself
            allowed_models (Union[str, Dict]): Allowed models, default is "all"
            remarks (str): Remarks, default is ""
        """
        return self.key.create_api_key(**kwargs)
    
    def delete_api_key(self, api_key_id: str):
        """
        Delete a key
        Note: Only admin can use this function
        """
        return self.key.delete_api_key(api_key_id=api_key_id)
    
    def verify_api_key(self, api_key: str, version: str = "v2"):
        return self.key.get_info(api_key=api_key, version = version)
    
    def fetch_api_key(self, username: str):
        """
        Fetch API Key by username
        """
        return self.key.fetch_api_key(username=username)
    
    ## --- 关于Agents的函数 --- ##
    def list_agents(self):
        """
        List all agents
        """
        return self.agents.list_agents()

class AsyncHepAIClient(AsyncHClient):
    """
    HepAI Client v2.0 (Asynchronous)

    Usage:
        ```python
        client = AsyncHepAIClient()
        await client.list_workers()
        ```
    """

    def __init__(
            self, 
            config: HClientConfig = None,
            **overrides,
            ):
        config = config or HClientConfig()
        super().__init__(config, **overrides)

        self.worker = resources.AsyncWorker(self)
        self.agents = resources.AsyncAgents(self)

        # TODO: AsyncUser and AsyncKey
        # self.key = resources.AsyncKey(self)
        # self.user = resources.AsyncUser(self)

    ## --- 关于Worker的函数 --- ## 
    async def list_workers(self):
        return await self.worker.list_workers()
    
    async def get_worker_info(
            self, 
            worker_id: str = None, 
            model_name: str = None,
            ) -> WorkerInfo:
        """
        Get worker info by worker_id via http request
        """
        return await self.worker.get_info(worker_id=worker_id, model_name=model_name)
    
    async def get_worker_status(self, worker_id: str, refresh: bool = False) -> WorkerStatusInfo:
        """
        Get worker status by worker_id via http request
        """
        return await self.worker.get_status(worker_id=worker_id, refresh=refresh)

    async def stop_worker(self, worker_id: str, permanent: bool = False) -> WorkerStoppedInfo:
        """
        Stop worker by worker_id via http request
        """
        return await self.worker.stop(worker_id=worker_id, permanent=permanent)

    async def refresh_all_workers(self) -> dict:
        """
        Refresh all workers
        """
        return await self.worker.refresh_all()
    
    async def get_remote_model(self, model_name: str) -> LRemoteModel:
        """
        Get a remote model
        """
        return await self.worker.get_remote_model(model_name=model_name)
    
    async def request_worker(
            self,
            target: dict,
            args: list = None,
            kwargs: dict = None,
            ):
        """
        Request worker via http request
        """
        return await self.worker.request(target=target, args=args, kwargs=kwargs)

    async def register_worker(
            self,
            model: HRemoteModel,
            daemon: bool = False,
            standalone: bool = False,
            ):
        """
        Register a worker to the server
        """
        return await self.worker.register(model, daemon=daemon, standalone=standalone)
    
    async def run_demo_worker_and_register(self):
        return await self.worker.register(standalone=True)

    ## # --- 关于User的函数 --- ##
    async def list_users(self):
        """
        List all users
        Note: Only admin can use this function
        """
        return await self.user.list_users()
    
    async def create_user(self, **kwargs):
        """
        Create a new user
        Note: Only admin can use this function
        """
        return await self.user.create_user(**kwargs)
    
    async def delete_user(self, user_id: str):
        """
        Delete a user
        Note: Only admin can use this function
        """
        return await self.user.delete_user(user_id=user_id)
    
    async def auth_user(self, username: str, password: str):
        """
        Auth a user by username and password
        """
        return await self.user.auth_user(username=username, password=password)

    ### --- 关于Key的函数 --- ###
    async def list_api_keys(self):
        """
        List all keys
        Note: Only admin can use this function
        """
        return await self.key.list_api_keys()
    
    async def create_api_key(self, **kwargs):
        """
        Create a new key
        Note: Only admin and app admin can use this function
        """
        return await self.key.create_api_key(**kwargs)
    
    async def delete_api_key(self, api_key_id: str):
        """
        Delete a key
        Note: Only admin can use this function
        """
        return await self.key.delete_api_key(api_key_id=api_key_id)
    
    async def verify_api_key(self, api_key: str, version: str = "v2"):
        return await self.key.get_info(api_key=api_key, version=version)
    
    ## --- 关于Agents的函数 --- ##
    async def list_agents(self):
        """
        List all agents asynchronously
        """
        return await self.agents.list_agents()