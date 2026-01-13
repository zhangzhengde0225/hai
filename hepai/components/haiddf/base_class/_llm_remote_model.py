import os
from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any, AsyncGenerator
from dataclasses import dataclass, field
import json

# from anthropic.types import Message

# from hepai import HepAI, AsyncHepAI
import httpx
from ..hepai_client import HepAIClient as HepAI
from ..hepai_client import AsyncHepAIClient as AsyncHepAI

from ._worker_class import HRModel, HModelConfig
# from hepai import HRModel, HWorkerAPP, HModelConfig, HWorkerConfig


class LLMRemoteModel(HRModel):
    def __init__(self, config: "LLMModelConfig"):
        super().__init__(config=config)
        self.cfg = config
        self.engine = config.engine

        self.enable_async = config.enable_async
        self._client = None
        self._async_client = None
        self._async_client_with_anthropic_url = None

    @property
    def client(self):
        if self._client is None:
            self._client = HepAI(
                base_url=self.cfg.base_url,
                api_key=self.cfg.api_key,
                proxy=self.cfg.proxy
            )
        return self._client
    
    @property
    def async_client(self):
        if self._async_client is None:
            self._async_client = AsyncHepAI(
                base_url=self.cfg.base_url,
                api_key=self.cfg.api_key,
                proxy=self.cfg.proxy
            )
        return self._async_client
    
    @property
    def async_client_with_anthropic_url(self):
        if self._async_client_with_anthropic_url is None:
            base_url = self.cfg.base_url
            # 去掉v1或v2等版本号
            if base_url.endswith("/v1") or base_url.endswith("/v2") or base_url.endswith("/v3"):
                base_url = base_url.rsplit("/", 1)[0]
            if not base_url.endswith("/anthropic"):
                if base_url.endswith("/"):
                    base_url = base_url + "anthropic"
                else:
                    base_url = base_url + "/anthropic"
            self._async_client_with_anthropic_url = AsyncHepAI(
                base_url=base_url,
                api_key=self.cfg.api_key,
                proxy=self.cfg.proxy
            )
        return self._async_client_with_anthropic_url
    
    def __repr__(self):
        return f"<LLMRemoteModel name={self.cfg.name} engine={self.cfg.engine} version={self.cfg.version}>"
    
    def get_models_from_config(self) -> List["LLMRemoteModel"]:
        """从配置文件读取模型，并实例化自己，形成许多个模型对象"""
        # 这里可以从配置文件中读取支持的模型列表
        # 示例配置，实际可以从外部配置文件读取
        supported_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "claude-3-sonnet",
            "claude-3-haiku"
        ]
        
        rm_models = []
        for model_name in supported_models:
            rm_config = LLMModelConfig(
                name=model_name,
                engine=model_name,
                base_url=self.cfg.base_url,
                _api_key=self.cfg.api_key,
                proxy=self.cfg.proxy,
                need_external_api_key=self.cfg.need_external_api_key
            )
            rm_models.append(LLMRemoteModel(config=rm_config))
        return rm_models
        
    @HRModel.remote_callable
    def custom_method(self, a: int, b: int) -> int:
        """你可以在这里定义你的自定义方法和返回值"""
        return a + b

    @property
    def oai_param_keys(self):
        return [
            "messages", "model", "frequency_penalty", 
            "function_call", "functions", "logit_bias", 
            "logprobs", "max_tokens", "n", 
            "presence_penalty", "response_format", 
            "seed", "stop", "stream", "stream_options", 
            "temperature", "tool_choice", "tools", 
            "top_logprobs", "top_p", "user", "extra_headers", 
            "extra_query", "extra_body", "timeout"]
    
    @property
    def is_o1(self):
        if "/" in self.engine:
            m = self.engine.split("/")[1]
        else:
            m = self.engine
        if m in ["o1", "o1-mini", "o1-preview"]:
            return True
        return False

    async def response_to_stream_async(self, response):
        """stream object to string generator"""
        async for chunk in response:
            chunk_data = chunk.model_dump()
            yield f'data: {json.dumps(chunk_data)}\n\n'

    def request_openai(
            self, 
            oai_messages: List,
            stream: bool = False,
            extra_headers: None = None,
            **kwargs):
        oai_params = {k: v for k, v in kwargs.items() if k in self.oai_param_keys}
        oai_params.pop("model", None)
        oai_params.pop("messages", None)
        extra_body: Dict = oai_params.pop("extra_body", {})
 
        response = self.client.chat.completions.create(
            model=self.engine, 
            messages=oai_messages, 
            stream=stream,
            extra_headers=extra_headers,
            extra_body=extra_body,
            **oai_params
            )
        return response
    
    async def request_openai_async(
            self, 
            oai_messages: List,
            stream: bool = False,
            extra_headers: None = None,
            **kwargs):
        oai_params = {k: v for k, v in kwargs.items() if k in self.oai_param_keys}
        oai_params.pop("model", None)
        oai_params.pop("messages", None)
        extra_body: Dict = oai_params.pop("extra_body", {})
        
        stream_options = oai_params.pop("stream_options", {})
        if stream:
            stream_options["include_usage"] = True  # 强制返回usage信息
        else:
            stream_options=HepAI.NotGiven
        response = await self.async_client.chat.completions.create(
            model=self.engine, 
            messages=oai_messages, 
            stream=stream,
            extra_headers=extra_headers,
            extra_body=extra_body,
            stream_options=stream_options,
            **oai_params
            )
        return response
    
        
    @HRModel.remote_callable
    async def chat_completions(self, *args, **kwargs):
        """openai的chat completions接口"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            extra_headers = kwargs.pop("extra_headers", {})

        oai_messages = kwargs.pop("messages")
        assert oai_messages, "messages is required"
        model = kwargs.pop("model", None)
        should_stream = kwargs.pop("stream", False)

        if self.is_o1:
            kwargs.pop("temperature", None)
            kwargs.pop("top_p", None)

        if should_stream:
            not_stream_to_str = kwargs.pop("not_stream_to_str", False)
            response = await self.request_openai_async(
                oai_messages=oai_messages,
                stream=True,
                extra_headers=extra_headers,
                **kwargs
            )
            if not_stream_to_str:
                return response
            else:
                gen = self.response_to_stream_async(response)
                return gen
        else:
            response = await self.request_openai_async(
                oai_messages=oai_messages,
                stream=False,
                extra_headers=extra_headers,
                **kwargs,
            )
            return response
        
    @HRModel.remote_callable
    async def embeddings(self, *args, **kwargs):
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            extra_headers = kwargs.pop("extra_headers", {})
        extra_body: Dict = kwargs.pop("extra_body", {})
        extra_query: Dict = kwargs.pop("extra_query", {})
        stream = kwargs.pop("stream", False)  # Embeddings一般不支持stream
        model = kwargs.pop("model", None)
        timeout = kwargs.pop("timeout", HepAI.NotGiven)

        # request = EmbeddingsRequest(**kwargs)
        input = kwargs.pop("input", None)
        
        response = await self.async_client.embeddings.create(
                input=input,
                model=self.cfg.engine,
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout,
                **kwargs
                )
        return response
    
    @HRModel.remote_callable
    async def rerank(self, *args, **kwargs):
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            extra_headers = kwargs.pop("extra_headers", {})
        extra_body: Dict = kwargs.pop("extra_body", {})
        extra_query: Dict = kwargs.pop("extra_query", {})
        stream = kwargs.pop("stream", False)
        timeout = kwargs.pop("timeout", HepAI.NotGiven)

        # request = RerankRequest(**kwargs)
        query = kwargs.pop("query", None)
        model = kwargs.pop("model", None)
        top_n = kwargs.pop("top_n", 3)
        documents = kwargs.pop("documents", None)
        return_documents = kwargs.pop("return_documents", False)

        headers = {
            "Content-Type": "application/json"
        }
        headers.update(extra_headers)
        data = {
            "model": self.cfg.engine,
            "query": query,
            "top_n": top_n,
            "documents": documents,
            "return_documents": return_documents,
            **extra_body
        }

        with httpx.Client() as client:
            response = client.post(
                f"{self.cfg.base_url}/rerank",
                headers=headers, 
                json=data)
            # 检查错误
            response.raise_for_status()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        return response.json()
    
    @HRModel.remote_callable
    async def image_generations(self, *args, **kwargs):
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            extra_headers = kwargs.pop("extra_headers", {})
        extra_body: Dict = kwargs.pop("extra_body", {})
        extra_query: Dict = kwargs.pop("extra_query", {})
        stream = kwargs.pop("stream", False)
        timeout = kwargs.pop("timeout", HepAI.NotGiven)

        # request = ImageGenerationRequest(**kwargs)
        prompt = kwargs.pop("prompt", None)
        

        response = await self.async_client.images.generate(
            prompt=prompt,
            model=self.cfg.engine,
            extra_headers=extra_headers,
            extra_body=extra_body,
            extra_query=extra_query,
            timeout=timeout,
            **kwargs
        )
        return response
    
    
    
    @HRModel.remote_callable
    async def anthropic_messages(self, *args, **kwargs) -> Union[Dict, AsyncGenerator]:
        """Anthropic Messages API接口"""
        modelx = kwargs.get("model")
        # if modelx == "claude-sonnet-4-20250514"
        # kwargs['stream'] = False  # Anthropic的接口不支持stream参数，这里强制设为False
        stream = kwargs.get("stream", False)
        
        # if any(x in modelx.lower() for x in ["moonshot", "openai", "kimi", "gpt", "claude"]):
        if any(x in modelx.lower() for x in ["moonshot", "openai", "kimi", "gpt"]):
        
            # 如果是moonshot或openai开头的模型，走openai接口
            from . import general
            oai_params = await general.convert_input_anthropic_to_openai_format(kwargs)
            if stream:
                oai_params.update({"not_stream_to_str": True})  # 强制返回对象，不转换为字符串流
                rst = await self.chat_completions(**oai_params)
                gen = general.convert_openai_to_anthropic_format_stream(rst, return_dict=False)
                return gen
            else:
                rst = await self.chat_completions(**oai_params)
                rst2 = await general.convert_object_openai_to_anthropic(rst)
                return rst2
        
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
            extra_headers = {"x-api-key": api_key}
        else:
            extra_headers = kwargs.pop("extra_headers", {})
        
        anthropic_version = kwargs.pop("anthropic_version", None)
        anthropic_beta = kwargs.pop("anthropic_beta", None)
        if anthropic_version:
            extra_headers["anthropic-version"] = anthropic_version
        if anthropic_beta:
            extra_headers["anthropic-beta"] = anthropic_beta
            
        extra_body: Dict = kwargs.pop("extra_body", {})
        extra_query: Dict = kwargs.pop("extra_query", {})
        timeout = kwargs.pop("timeout", None)
        
        if "model" not in kwargs:
            raise ValueError("model parameter is required")
        if "messages" not in kwargs:
            raise ValueError("messages parameter is required")
        if "max_tokens" not in kwargs:
            raise ValueError("max_tokens parameter is required")
            
        modelx = kwargs.pop("model")
        messages = kwargs.pop("messages")
        max_tokens = kwargs.pop("max_tokens")
        # if max_tokens == 500:
        #     pass
        thinking = kwargs.get("thinking", {})
        # Deal with maxtokens if thinking is enabled
        if thinking.get("type") == "enabled":
            budget_tokens = thinking.get("budget_tokens", 0)
            max_tokens = max(max_tokens, budget_tokens+1)
    
        stream = kwargs.pop("stream", False)
        # kwargs.pop("context_management", None)  # 去掉context_management参数，避免报错
        
        """
        # 20251209左右，系统提示词里包含"cahce_control": {'type': 'ephemeral'}，智增增会报错
        system = kwargs.pop("system", None)
        if system:
            # 移除system消息中的cache_control字段，相当于永远不缓存，会增加开销
            for sys_msg in system:
                if "cache_control" in sys_msg:
                    sys_msg.pop("cache_control")
        # messages里也有可能有缓存字段
        if messages:
            for msg in messages:
                if "cache_control" in msg:
                    msg.pop("cache_control")
                for content in msg.get("content", []):
                    if isinstance(content, dict) and "cache_control" in content:
                        content.pop("cache_control")
        # kwargs.pop("tools", None)  # 去掉tools参数，避免报错
        # kwargs.pop("metadata", None)  # 去掉metadata参数，避免报错
        # kwargs.pop("thinking", None)  # 去掉thinking参数，避免报错
        # kwargs.pop("temperature", None)  # 去掉temperature参数，避免报错
        """
        
        if stream:
            pass
            # thinking = kwargs.get("thinking", {})

            # print(f"max_tokens: {max_tokens}, thinking: {thinking}")
            # if max_tokens == 500:
            #     pass
            gen = self.anthropic_stream(
                model=self.cfg.engine,
                messages=messages,
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout,
                **kwargs
                )
            
            return gen
        else:
            
            rst = await self.async_client_with_anthropic_url.anthropic.messages.create(
                    model=self.cfg.engine,
                    messages=messages,
                    max_tokens=max_tokens,
                    stream=stream,
                    extra_headers=extra_headers,
                    extra_body=extra_body,
                    extra_query=extra_query,
                    timeout=timeout,
                    **kwargs
                )
            # rst = rst.model_dump()
            if rst.type == 'error':
                error_info = rst.model_extra.get('error', {})
                raise ValueError(f"Anthropic API Error: {error_info}")
            return rst
        
    async def anthropic_stream(
            self,
            model,
            messages,
            max_tokens,
            extra_headers=None,
            extra_body=None,
            extra_query=None,
            timeout=None,
            **kwargs) -> AsyncGenerator:
        
        async with self.async_client_with_anthropic_url.anthropic.messages.stream(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
            extra_body=extra_body,
            extra_query=extra_query,
            timeout=timeout,
            **kwargs
            ) as async_message_stream:
            # i = 0
            async for chunk in async_message_stream:
                # print(f"{i} {chunk}")
                # i += 1
                data = chunk.model_dump()
                yield f"event: {chunk.type}\ndata: {json.dumps(data)}\n\n"
     
    @HRModel.remote_callable
    async def anthropic_count_tokens(self, *args, **kwargs) -> Dict:
        """Anthropic Count Tokens API接口"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
            extra_headers = {"x-api-key": api_key}
        else:
            extra_headers = kwargs.pop("extra_headers", {})
        
        extra_body: Dict = kwargs.pop("extra_body", {})
        extra_query: Dict = kwargs.pop("extra_query", {})
        timeout = kwargs.pop("timeout", None)
        
        if "model" not in kwargs:
            raise ValueError("model parameter is required")
        if "messages" not in kwargs:
            raise ValueError("messages parameter is required")
            
        modelx = kwargs.pop("model")
        messages = kwargs.pop("messages")
        
        message_tokens_count = await self.async_client_with_anthropic_url.anthropic.messages.count_tokens(
                messages=messages,
                model=self.cfg.engine,
                
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout,
                **kwargs
            )
        return message_tokens_count



     
@dataclass
class LLMModelConfig(HModelConfig):
    config_file: str = field(default=None, metadata={"help": "Model's config file path"})
    name: str = field(default="openai/gpt-image-1", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    engine: str = field(default="gpt-image-1", metadata={"help": "Model engine"})
    base_url: str = field(default="https://api.zhizengzeng.com/v1", metadata={"help": "Base url of the zhizengzeng API"})
    _api_key: str = field(default="os.environ/ZHIZENGZENG_API_KEY", metadata={"help": "API key of the model"})
    proxy: str = field(default=None, metadata={"help": "Proxy of the model"})
    need_external_api_key: bool = field(default=False, metadata={"help": "Need external api key from user, if True, each request must provide api_key parameter"})
    enable_async: bool = field(default=True, metadata={"help": "whether use async client"})
    test: bool = field(default=False, metadata={"help": "Test model"})

    def __post_init__(self):
        if isinstance(self._api_key, str) and self._api_key.startswith("os.environ/"):
            environ_name = self._api_key.split("/")[1]
            self._api_key = os.getenv(environ_name)
    
    @property
    def api_key(self):
        return self._api_key