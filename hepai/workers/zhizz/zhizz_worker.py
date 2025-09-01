import os
from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any
from dataclasses import dataclass, field
import uvicorn
import hepai as hai
from hepai import HepAI
import json
from hepai import HRModel, HWorkerAPP, HModelConfig, HWorkerConfig
from _message_class import (
    Usage, DeltaMessage, ChatMessage, ChatCompletionRequest,
    EmbeddingsRequest, ImageGenerationRequest
)
from fastapi.exceptions import HTTPException


from pathlib import Path
here = Path(__file__).parent
from dotenv import load_dotenv
load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量


class ZhizzRemoteModel(HRModel):
    def __init__(self, config: "ZhizzModelConfig"):
        super().__init__(config=config)
        self.cfg = config
        self.engine = config.engine
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = HepAI(
                base_url=self.cfg.base_url,
                api_key=self.cfg.api_key,
                proxy=self.cfg.proxy
            )
        return self._client
    
    def get_models_from_config(self) -> List["ZhizzRemoteModel"]:
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
            rm_config = ZhizzModelConfig(
                name=model_name,
                engine=model_name,
                base_url=self.cfg.base_url,
                _api_key=self.cfg.api_key,
                proxy=self.cfg.proxy,
                need_external_api_key=self.cfg.need_external_api_key
            )
            rm_models.append(ZhizzRemoteModel(config=rm_config))
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

    def response_to_stream(self, response):
        for chunk in response:
            chunk_data = chunk.model_dump()
            yield f'data: {json.dumps(chunk_data)}\n\n'
            
            # print(chunk_data)  # Debugging output, can be removed later

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
        
        print(oai_params)
        
        response = self.client.chat.completions.create(
            model=self.engine, 
            messages=oai_messages, 
            stream=stream,
            extra_headers=extra_headers,
            extra_body=extra_body,
            **oai_params
            )
        return response

    @HRModel.remote_callable
    def chat_completions(self, *args, **kwargs):
        """openai的chat completions接口"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling zhizz worker")
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
            response = self.request_openai(
                oai_messages=oai_messages,
                stream=True,
                extra_headers=extra_headers,
                **kwargs
            )
            gen: Generator = self.response_to_stream(response)
            return gen
        else:
            response = self.request_openai(
                oai_messages=oai_messages,
                stream=False,
                extra_headers=extra_headers,
                **kwargs,
            )
            return response
        
    @HRModel.remote_callable
    def embeddings(self, *args, **kwargs):
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

        request = EmbeddingsRequest(**kwargs)

        response = self.client.embeddings.create(
                input=request.input,
                model=self.cfg.engine,
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout
                )
        return response
    
    @HRModel.remote_callable
    def image_generations(self, *args, **kwargs):
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

        request = ImageGenerationRequest(**kwargs)

        response = self.client.images.generate(
            prompt=request.prompt,
            model=self.cfg.engine,
            n=request.n,
            quality=request.quality,
            size=request.size,
            style=request.style,
            extra_headers=extra_headers,
            extra_body=extra_body,
            extra_query=extra_query,
            timeout=timeout,
        )
        return response
    
    @HRModel.remote_callable
    def anthropic_messages(self, *args, **kwargs):
        """Anthropic Messages API接口"""
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
            
        model = kwargs.pop("model")
        messages = kwargs.pop("messages")
        max_tokens = kwargs.pop("max_tokens")
        stream = kwargs.pop("stream", False)
        
        response = self.client.anthropic.messages.create(
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
        
        if stream:
            gen: Generator = self.response_to_stream(response)
            return gen
        else:
            return response
        
def test_model():
    api_key = os.getenv("ZHIZENGZENG_API_KEY")
    
    model = "gpt-4.1"
    zhizz_model = ZhizzRemoteModel(config=ZhizzModelConfig(engine=model))
    stream = False  # Set to True if you want to test streaming
    stream = True
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": "say hello"}],
        "stream": stream,
        "api_key": api_key,
        "stream_options": {"include_usage": True},
    }
    rst = zhizz_model.chat_completions(**kwargs)
    if stream:
        for chunk in rst:
            print(chunk)
    else:
        print(rst)


    

@dataclass
class ZhizzModelConfig(HModelConfig):
    # config_file: str = field(default=f"{here}/model_config.yaml", metadata={"help": "Model's config file path"})
    config_file: str = field(default=None, metadata={"help": "Model's config file path"})
    name: str = field(default="openai/gpt-image-1", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    engine: str = field(default="gpt-image-1", metadata={"help": "Model engine"})
    base_url: str = field(default="https://api.zhizengzeng.com/v1", metadata={"help": "Base url of the zhizengzeng API"})
    _api_key: str = field(default="os.environ/ZHIZENGZENG_API_KEY", metadata={"help": "API key of the model"})
    proxy: str = field(default=None, metadata={"help": "Proxy of the model"})
    need_external_api_key: bool = field(default=False, metadata={"help": "Need external api key from user，就是每次发送请求都需要外部传输过来"})
    use_async: bool = field(default=True, metadata={"help": "whether use async client"})
    test: bool = field(default=True, metadata={"help": "Test model"})

    def __post_init__(self):
        if isinstance(self._api_key, str) and self._api_key.startswith("os.environ/"):
            environ_name = self._api_key.split("/")[1]
            self._api_key = os.getenv(environ_name)
    
    @property
    def api_key(self):
        return self._api_key

@dataclass
class ZhizzWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=0, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: payg', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a zhizz worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    author: str = field(default=None, metadata={"help": "Model's author"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(default=100, metadata={"help": "Limit the model's concurrency"})


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hai.parse_args((ZhizzModelConfig, ZhizzWorkerConfig))
    
    if model_config.test:
        test_model()
        # exit(0)
    
    from hepai.workers.zhizz.utils import load_models

    models: List[ZhizzRemoteModel] = load_models(model_config)  # Load models from the configuration file.
    app: FastAPI = HWorkerAPP(models, worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.

    wk_info = app.worker.get_worker_info()
    print(wk_info, flush=True)
    # 打印一下模型：
    print(f"🚀 Worker is running. {len(wk_info.resource_info)} available models:")
    # m_names = [m.model_name for m in wk_info.resource_info]
    # print_mns = m_names if len(m_names) <= 10 else m_names[:5] + ["..."] + m_names[-5:]
    # for m in print_mns:
    #     print(f"    - Model: {m}")
        # print(f" - Model: {m['name']}, Engine: {m.get('engine', 'N/A')}, Version: {m.get('version', 'N/A')}, Permission: {m.get('permission', 'N/A')}", flush=True)
    # 启动服务
    uvicorn.run(app, host=app.host, port=app.port)
    