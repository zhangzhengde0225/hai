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

    async def anthropic_messages(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[AnthropicRouterGroup] This `model` must be specified")
        model = request_body["model"]
        self.count += 1
        func_params = FunctionParamsItem(
            args=[],
            kwargs=request_body
        )
        rst = await self.parent_app.worker_unified_gate(
            function_params=func_params,
            model=model, 
            function="anthropic_messages",
        )
        return rst

    async def count_tokens(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[AnthropicRouterGroup] This `model` must be specified")
        model = request_body["model"]
        self.count += 1
        func_params = FunctionParamsItem(
            args=[],
            kwargs=request_body
        )
        rst = await self.parent_app.worker_unified_gate(
            function_params=func_params,
            model=model,
            function="count_tokens",
        )
        return rst