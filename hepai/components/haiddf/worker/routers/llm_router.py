from typing import List, Callable, Dict
from dataclasses import field, dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi import FastAPI

# from ..auth.authorizer import HAuthorizer, HAPIKeyAuth
# from ...configs.model_aliases import model_aliases_to_real_name
# from ...utils.http_parsing_util import read_request_body
# from ...utils._logger import Logger, save_minitor_log
# from ...utils import general
from .._worker_class import CommonWorker
from ..utils import(
    read_request_body
    )
from ..worker_app import HWorkerAPP, FunctionParamsItem
from ..singletons import authorizer

# logger = Logger.get_logger("llm_router_group")
# api_key_auth: Callable = Depends(HAuthorizer().api_key_auth)
api_key_auth: Callable = Depends(authorizer.api_key_auth)


@dataclass
class LLMRouterGroup:
    name: str = "llm"
    prefix: str = "/apiv2"
    tags: List[str] = field(default_factory=lambda: ["llm"])
    router: APIRouter = field(default_factory=APIRouter)
    parent_app: HWorkerAPP = None  # type: ignore

    def __post_init__(self):
        # super().__post_init__()
        
        self.count = 0
        
        rt = self.router
        rt.post("/completions", dependencies=[api_key_auth])(self.chat_completions)
        rt.post("/v1/completions", dependencies=[api_key_auth])(self.chat_completions)
        rt.post("/chat/completions", dependencies=[api_key_auth])(self.chat_completions)
        rt.post("/v1/chat/completions", dependencies=[api_key_auth])(self.chat_completions)
        rt.post("/v1/embeddings", dependencies=[api_key_auth])(self.embeddings)
        rt.post("/embeddings", dependencies=[api_key_auth])(self.embeddings)
        rt.get("/models", dependencies=[api_key_auth])(self.list_models)
        rt.get("/v1/models", dependencies=[api_key_auth])(self.list_models)
        rt.post("/images/generations", dependencies=[api_key_auth])(self.image_generations)
        rt.post("/v1/images/generations", dependencies=[api_key_auth])(self.image_generations)

    async def chat_completions(self, request: Request):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[LLMRouterGroup] This `model` must be specified")
        model = request_body["model"]
        # if "claude" in model.lower():
        #     transformed, model = model_aliases_to_real_name(model)
        #     if transformed:
        #         request_body["model"] = model
        #     if "claude" in model.lower():
        #         request_body["stream"] = False
        #     if "max_tokens" not in request_body:
        #         request_body["max_tokens"] = 2048
        #     function = "anthropic_messages"
        #     postprocess_funcs = [general.convert_claude_to_openai_format]
        # else:
        #     function = "chat_completions"
        #     postprocess_funcs = []
        # if user_auth.resc_attr.resource_type == "worker":
        #     request_body = self.update_request_body_for_worker(request_body, user_auth)
        self.count += 1
        # await save_minitor_log(logger, user_auth)
        func_params = FunctionParamsItem(
            args=[],
            kwargs=request_body
        )
        rst = await self.parent_app.worker_unified_gate(
            function_params=func_params,
            model=model, 
            function="chat_completions",
        )
        # if postprocess_funcs:
        #     for func in postprocess_funcs:
        #         rst = await func(rst)
        return rst

    async def embeddings(self, request: Request, user_auth = api_key_auth):
        request_body: Dict = await read_request_body(request=request)
        if "model" not in request_body:
            raise HTTPException(status_code=400, detail="[LLMRouterGroup] This `model` must be specified")
        model = request_body["model"]
        if user_auth.resc_attr.resource_type == "worker":
            request_body = self.update_request_body_for_worker(request_body, user_auth)
        self.count += 1
        await save_minitor_log(logger, user_auth)
        return await self.worker.unified_gate_async(
            model=model, 
            function="embeddings",
            args=[],
            kwargs=request_body,
        )

    async def list_models(self, user_auth = api_key_auth):
        return await self.parent_app.get_models()

    async def image_generations(self, request: Request, user_auth = api_key_auth):
        request_body: Dict = await read_request_body(request=request)
        if "prompt" not in request_body:
            raise HTTPException(status_code=400, detail="[LLMRouterGroup] The 'prompt' field is required")
        if "model" not in request_body:
            request_body["model"] = "dall-e-2"
        model = request_body["model"]
        valid_models = ["dall-e-2", "dall-e-3", "gpt-image-1"]
        model_without_prefix = model.split("/")[-1]
        if model_without_prefix not in valid_models:
            raise HTTPException(status_code=400, detail=f"[LLMRouterGroup] Invalid model '{model}'. Must be one of {valid_models}")
        prompt = request_body["prompt"]
        max_lengths = {"gpt-image-1": 32000, "dall-e-2": 1000, "dall-e-3": 4000}
        if len(prompt) > max_lengths[model_without_prefix]:
            raise HTTPException(status_code=400, detail=f"[LLMRouterGroup] Prompt too long for {model}. Maximum length is {max_lengths[model]} characters")
        request_body.setdefault("n", 1)
        request_body.setdefault("size", "auto" if model_without_prefix == "gpt-image-1" else "1024x1024")
        request_body.setdefault("quality", "auto")
        request_body.setdefault("response_format", "url")
        if model_without_prefix == "dall-e-3" and request_body["n"] != 1:
            raise HTTPException(status_code=400, detail="[LLMRouterGroup] For dall-e-3, only n=1 is supported")
        if request_body["n"] < 1 or request_body["n"] > 10:
            raise HTTPException(status_code=400, detail="[LLMRouterGroup] n must be between 1 and 10")
        if user_auth.resc_attr.resource_type == "worker":
            request_body = self.update_request_body_for_worker(request_body, user_auth)
        self.count += 1
        await save_minitor_log(logger, user_auth)
        return await self.worker.unified_gate_async(
            model=model, 
            function="image_generations",
            args=[],
            kwargs=request_body,
        )

    def update_request_body_for_worker(self, request_body: Dict, user_auth) -> Dict:
        resc = user_auth.resc_attr.resource
        if resc.type == "litellm":
            request_body["api_key"] = user_auth.api_key
            request_channel = user_auth.resc_attr.request_channel.name
            request_body["extra_body"] = {
                "user": user_auth.user_attr.username,
                "metadata": {"tags": [f"channelTag: {request_channel}"]}
            }
        elif resc.type == "drsai":
            u = user_auth.user_attr
            user_info_dict = {
                "id": u.id,
                "username": u.username,
                "user_level": u.user_level.to_str(),
                "user_groups": [g.name for g in u.user_groups],
                "email": u.email,
                "balance": u.balance,
                "api_key": user_auth.api_key
            }
            request_body["extra_body"] = {
                "user": user_info_dict,
                "base_models": "deepseek/deepseek-v3",
            }
        return request_body
    
    