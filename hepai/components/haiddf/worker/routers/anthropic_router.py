from typing import List, Callable, Dict
from dataclasses import field, dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi import FastAPI

from .._worker_class import CommonWorker
from ..utils import(
    read_request_body
    )
from ..worker_app import HWorkerAPP, FunctionParamsItem
from ..singletons import authorizer

from hepai.workers.zhizz.utils import get_provider_by_model_name

api_key_auth: Callable = Depends(authorizer.api_key_auth)


@dataclass
class AnthropicRouterGroup:
    name: str = "anthropic"
    prefix: str = "/apiv2"
    tags: List[str] = field(default_factory=lambda: ["anthropic"])
    router: APIRouter = field(default_factory=APIRouter)
    parent_app: HWorkerAPP = None  # type: ignore

    def __post_init__(self):
        
        self.count = 0
        rt = self.router
        rt.post("/anthropic/messages", dependencies=[api_key_auth])(self.anthropic_messages)
        rt.post("/anthropic/v1/messages", dependencies=[api_key_auth])(self.anthropic_messages)
        rt.post("/anthropic/v1/messages/count_tokens", dependencies=[api_key_auth])(self.count_tokens)

        rt.post("/anthropic/api/event_logging/batch", dependencies=[api_key_auth])(self.event_logging_batch)
        rt.post("/anthropic//api/event_logging/batch", dependencies=[api_key_auth])(self.event_logging_batch)

    async def event_logging_batch(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        # print(f"Received event logging batch:")
        # import json
        # print(json.dumps(request_body, indent=2), flush=True)
        pass

    async def anthropic_messages(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[AnthropicRouterGroup] This `model` must be specified")
        
        # Auto rename
        model = request_body["model"]
        if '/' not in model:
            model_name = f'{get_provider_by_model_name(model)}/{model}'
        else:
            model_name = model
        
        self.count += 1
        func_params = FunctionParamsItem(
            args=[],
            kwargs=request_body
        )
        rst = await self.parent_app.worker_unified_gate(
            function_params=func_params,
            model=model_name, 
            function="anthropic_messages",
        )
        return rst

    async def count_tokens(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[AnthropicRouterGroup] This `model` must be specified")
        model = request_body["model"]
        
        # Auto rename
        model = request_body["model"]
        if '/' not in model:
            model_name = f'{get_provider_by_model_name(model)}/{model}'
        else:
            model_name = model
        

        self.count += 1
        func_params = FunctionParamsItem(
            args=[],
            kwargs=request_body
        )
        rst = await self.parent_app.worker_unified_gate(
            function_params=func_params,
            model=model_name,
            function="anthropic_count_tokens",
        )
        return rst