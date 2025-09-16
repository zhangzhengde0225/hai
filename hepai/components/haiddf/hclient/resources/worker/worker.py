
from typing import Dict, Any
import io
from ..._types import Stream
from .._resource import SyncAPIResource, AsyncAPIResource

from ..._return_class import (
    HWorkerListPage,
)
from ..._related_class import (
    WorkerInfo, HRemoteModel, WorkerStoppedInfo, WorkerStatusInfo,
)

# from ...openai_api._base_client import make_request_options
from openai._base_client import make_request_options


class Worker(SyncAPIResource):

    @property
    def prefix(self) -> str:
        return "/worker"
    
    def list_workers(self):
        return self._get(
            f"{self.prefix}/list_workers",
            cast_to=HWorkerListPage,
        )

    def get_info(
            self,
            worker_id: str = None,
            model_name: str = None,
            ) -> WorkerInfo:
        assert worker_id or model_name, "Either worker_id or model_name should be provided."
        payload = {
            "worker_id": worker_id,
            "model_name": model_name,
        }
        return self._post(
            f"{self.prefix}/get_worker_info",
            cast_to=WorkerInfo,
            body=payload,
        )

    def get_status(
            self,
            worker_id: str,
            refresh: bool = False,
            ) -> WorkerStatusInfo:
        payload = {
            "worker_id": worker_id,
            "refresh": refresh,
        }
        return self._post(
            f"{self.prefix}/get_worker_status",
            cast_to=WorkerStatusInfo,
            body=payload,
        )
    
    def stop(
            self,
            worker_id: str,
            permanent: bool = False,
            ) -> WorkerStoppedInfo:
        payload = {
            "worker_id": worker_id,
            "permanent": permanent,
        }
        return self._post(
            f"{self.prefix}/stop_worker",
            cast_to=WorkerStoppedInfo,
            body=payload,
        )
    
    def refresh_all(self):
        return self._get(
            f"{self.prefix}/refresh_all_workers",
            cast_to=Dict[str, Any],
        )
    
    def get_remote_model(
            self,
            worker_id: str = None,
            model_name: str = None,
            ) -> HRemoteModel:
        worker_info: WorkerInfo = self.get_info(worker_id=worker_id, model_name=model_name)
        if not isinstance(worker_info, WorkerInfo):
            raise ValueError(f"Failed to get remote model: {worker_info}")
        from ..._remote_model import LRemoteModel
        return LRemoteModel(name=model_name, worker_info=worker_info, worker_resource=self)

    def request(
            self,
            target: dict,  # 请求目标模型和函数, such as {"model": model_name, "function": "__call__"}
            args: list = None, 
            kwargs: dict = None,
        ):
        # get model and function
        model = target.get("model")
        function = target.get("function")  
        # check if need stream
        stream = kwargs.get("stream", False) if kwargs is not None else False

        from typing import cast, Mapping
        from openai._utils import deepcopy_minimal, extract_files      
        
        # set payload
        payload = dict()
        if args:
            payload["args"] = args
        if kwargs:
            payload["kwargs"] = kwargs
        
        # 适配文件上传，可从file字段中提取文件
        files = extract_files(cast(Mapping[str, object], kwargs), paths=[["file"]])
        payload = deepcopy_minimal(payload)
        
        # if True:
        #     payload = {'function_params': payload}
        
        extra_headers = None  # Headers
        extra_query = None  # Query
        extra_body = None  # Body
        # timeout = : float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        
        if files:
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        if stream:
            return self._post(
                f"{self.prefix}/unified_gate/?model={model}&function={function}",
                body=payload,
                stream=True,
                stream_cls=Stream[Any],
                cast_to=Any,
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body
            ),
            )
        return self._post(
            f"{self.prefix}/unified_gate/?model={model}&function={function}",
            cast_to=Any,
            body=payload,
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body
            ),
        )
    
    def register(
            self,
            model: HRemoteModel = None,
            daemon: bool = False,
            standalone: bool = False,
            )  -> WorkerInfo:
        
        from hepai import HWorkerAPP
        return HWorkerAPP.register_worker(model=model, daemon=daemon, standalone=standalone)
    

class AsyncWorker(AsyncAPIResource):
    """
    Asynchronous version of the Worker resource.
    """

    @property
    def prefix(self) -> str:
        return "/worker"

    async def list_workers(self) -> HWorkerListPage:
        """
        List all workers asynchronously.
        """
        return await self._get(
            f"{self.prefix}/list_workers",
            cast_to=HWorkerListPage,
        )

    async def get_info(
        self,
        worker_id: str = None,
        model_name: str = None,
    ) -> WorkerInfo:
        """
        Get worker info by `worker_id` or `model_name` asynchronously.
        Either worker_id or model_name should be provided.
        """
        assert worker_id or model_name, "Either worker_id or model_name should be provided."
        payload = {
            "worker_id": worker_id,
            "model_name": model_name,
        }
        return await self._post(
            f"{self.prefix}/get_worker_info",
            cast_to=WorkerInfo,
            body=payload,
        )

    async def get_status(
        self,
        worker_id: str,
        refresh: bool = False,
    ) -> WorkerStatusInfo:
        """
        Get worker status by `worker_id` asynchronously.
        Set `refresh` to True to refresh the worker status.
        """
        payload = {
            "worker_id": worker_id,
            "refresh": refresh,
        }
        return await self._post(
            f"{self.prefix}/get_worker_status",
            cast_to=WorkerStatusInfo,
            body=payload,
        )

    async def stop(
        self,
        worker_id: str,
        permanent: bool = False,
    ) -> WorkerStoppedInfo:
        """
        Stop a worker by `worker_id` asynchronously.
        If `permanent` is True, stop the worker permanently.
        """
        payload = {
            "worker_id": worker_id,
            "permanent": permanent,
        }
        return await self._post(
            f"{self.prefix}/stop_worker",
            cast_to=WorkerStoppedInfo,
            body=payload,
        )

    async def refresh_all(self) -> Dict[str, Any]:
        """
        Refresh all workers asynchronously.
        """
        return await self._get(
            f"{self.prefix}/refresh_all_workers",
            cast_to=Dict[str, Any],
        )

    async def get_remote_model(
        self,
        worker_id: str = None,
        model_name: str = None,
    ) -> HRemoteModel:
        """
        Get a remote model by `worker_id` or `model_name` asynchronously.
        """
        worker_info: WorkerInfo = await self.get_info(
            worker_id=worker_id,
            model_name=model_name,
        )
        if not isinstance(worker_info, WorkerInfo):
            raise ValueError(f"Failed to get remote model: {worker_info}")
        from ..._remote_model import LRemoteModel
        return LRemoteModel(name=model_name, worker_info=worker_info, worker_resource=self)

    async def request(
        self,
        target: dict,
        args: list = None,
        kwargs: dict = None,
    ):
        """
        Request the target worker model and function asynchronously.
        `target` is a dict, for example: {"model": "HRemoteModel", "function": "hello_world"}.
        """
        model = target.get("model")
        function = target.get("function")
        stream = kwargs.get("stream", False) if kwargs else False
        payload = {}

        if args:
            payload["args"] = args
        if kwargs:
            payload["kwargs"] = kwargs

        if stream:
            return await self._post(
                f"{self.prefix}/unified_gate/?model={model}&function={function}",
                body=payload,
                stream=True,
                stream_cls=Stream[Any],
                cast_to=Any,
            )
        return await self._post(
            f"{self.prefix}/unified_gate/?model={model}&function={function}",
            cast_to=Any,
            body=payload,
        )

    async def register(
        self,
        model: HRemoteModel = None,
        daemon: bool = False,
        standalone: bool = False,
    ) -> WorkerInfo:
        """
        Register a worker to the server asynchronously.
        """
        from hepai import HWorkerAPP
        # If HWorkerAPP.register_worker is purely synchronous,
        # we just call it directly. If there's an async method, use await accordingly.
        return HWorkerAPP.register_worker(model=model, daemon=daemon, standalone=standalone)