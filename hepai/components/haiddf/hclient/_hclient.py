"""
基于OAI的SyncAPI的Client
"""

import os
import json
from typing import Mapping, Generator, Dict, AsyncGenerator
from typing_extensions import override
import httpx
import warnings


from .openai_api import *

from .resources._resource import SyncAPIResource
from ._exceptions import HAPIStatusError

# from . import resources
from dataclasses import dataclass, field, asdict

class DemoResoure(SyncAPIResource):
    """
    This is a demo resource for demostrating how to use SyncAPIResource
    
    Usage:
        ```python
        class MyClient(HClient):
            
            def __init__(self):
                super().__init__()
                self.demo_resource: SyncAPIResource = DemoResoure()
        ```

        ```python
        client = MyClient()
        client.demo_resource.get_index()
        ```
    """
    def get_index(self):
        return self._get(
            "/",
            cast_to=Any,
        )
    
    def post_index(self, data):
        return self._post(
            "/",
            cast_to=Any,
            body=data,
        )
    

def get_defualt_timeout(timeout: float = 600.0, connect: float = 5.0) -> httpx.Timeout:
    return httpx.Timeout(timeout=timeout, connect=connect)


# DEFAULT_BASE_URL = os.environ.get("HEPAI_BASE_URL", None)
# DEFAULT_API_KEY = os.environ.get("HEPAI_API_KEY", None)

@dataclass
class HClientConfig:
    # base_url: str = field(default=NOT_GIVEN, metadata={"description": "The default base URL for all requests"})
    base_url: str = field(default="https://aiapi.ihep.ac.cn/apiv2", metadata={"description": "The default base URL for all requests"})
    api_key: str = field(default=NOT_GIVEN, metadata={"description": "The default API key for all requests"})
    max_retries: int = field(default=0, metadata={"description": "The default maximum number of retries for all requests"})
    timeout: None | httpx.Timeout = field(default_factory=get_defualt_timeout, metadata={"description": "The default timeout for all requests"})
    http_client: None | httpx.Client  = field(default=None, metadata={"description": "The default HTTP client for all requests"})
    default_headers: Mapping[str, str] = field(default=None, metadata={"description": "The default headers for all requests"})
    default_query: Mapping[str, object] = field(default=None, metadata={"description": "The default query parameters for all requests"})
    enable_openai: bool = field(default=True, metadata={"description": "Whether to enable openai resources"})
    enable_anthropic: bool = field(default=True, metadata={"description": "Whether to enable anthropic resources"})
    proxy: str = field(default=None, metadata={"description": "The default proxy for all requests"})

    max_connections: int = field(default=1000, metadata={"description": "The maximum number of connections to keep open"})
    max_keepalive_connections: int = field(default=100, metadata={"description": "The maximum number of idle connections to keep open"})
    
    version: str = field(default="2.0.0", metadata={"description": "The version of the client"})
    _strict_response_validation: bool = field(default=False, metadata={"description": "Whether to strictly validate responses"})
    
    
    def __post_init__(self):
        # 尝试从环境变量获取API-KEY
        if self.api_key == NOT_GIVEN:
            key_in_env = os.environ.get("HEPAI_API_KEY", None)
            if key_in_env is not None:
                self.api_key = key_in_env
            
    
    def to_dict(self):
        return asdict(self)
    
    def update_by_dict(self, d: dict):
        unknown_keys = []
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                unknown_keys.append(k)
        if unknown_keys:
            warnings.warn(f"[HClientConfig] encountered {len(unknown_keys) } unknown keys when updating config, this keys will be ignored: {unknown_keys}")
        return self
    
    def instantiate_http_client(self,) -> httpx.Client:
        """如果http_client为None，则实例化一个httpx.Client"""
        if self.http_client is None:
            # proxies = None if self.proxy is None else {"https://": self.proxy, "http://": self.proxy}
            limits = httpx.Limits(max_connections=self.max_connections, max_keepalive_connections=self.max_keepalive_connections)
            self.http_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                # proxies=proxies,
                proxy=self.proxy,
                transport=None,
                limits=limits,
                follow_redirects=True,
            )
        return self.http_client


class HClient(SyncAPIClient):
    """
    高能AI框架基础客户端
    """
    NotGiven = NOT_GIVEN

    def __init__(
            self,
            config: HClientConfig = None,
            **overrides, # 用于覆盖默认配置
    ):
        self.config = config or HClientConfig()
        if overrides:
            self.config.update_by_dict(overrides)
        
        api_key = self.config.api_key
        if api_key == NOT_GIVEN:  # 人为设置为NOT_GIVEN时，不报错
            pass
        elif api_key is None:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the environment variable"
            )
        self.api_key = api_key


        if self.config.base_url == NOT_GIVEN:
            self.config.base_url = httpx.URL("")
            pass
        elif self.config.base_url is None:
            raise ValueError(
                "The base_url client option must be set, you can set it by passing base_url to the client or by setting the environment variable"
            )
        
        if (self.config.proxy is not None) and (self.config.http_client is None):
            print(f'[HClient] Proxy: {self.config.proxy}')
            self.config.instantiate_http_client()  # 提前实例化http_client，就设置了proxy

        super().__init__(
            version=self.config.version,
            base_url=self.config.base_url,
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
            http_client=self.config.http_client,
            custom_headers=self.config.default_headers,
            custom_query=self.config.default_query,
            _strict_response_validation=self.config._strict_response_validation,
        )

        if self.config.enable_openai:
            """集成openai的resources"""
            # from openai import OpenAI
            # from openai import resources
            # from openai._client import OpenAIWithRawResponse, OpenAIWithStreamedResponse
            from .openai_api import resources
            # self._default_stream_cls = HClient.Stream
            self.completions = resources.Completions(self)
            self.chat = resources.Chat(self)
            self.embeddings = resources.Embeddings(self)
            self.files = resources.Files(self)
            self.images = resources.Images(self)
            self.audio = resources.Audio(self)
            self.moderations = resources.Moderations(self)
            self.models = resources.Models(self)
            self.fine_tuning = resources.FineTuning(self)
            self.beta = resources.Beta(self)
            self.batches = resources.Batches(self)
            self.uploads = resources.Uploads(self)
            # self.with_raw_response = OpenAIWithRawResponse(self)
            # self.with_streaming_response = OpenAIWithStreamedResponse(self)

        if self.config.enable_anthropic:
            """集成anthropic的resources"""
            # from openai import resources
            # from openai._client import OpenAIWithRawResponse, OpenAIWithStreamedResponse
            # from .anthropic_api import resources
            # # self._default_stream_cls = HClient.Stream
            # self.anthropic = resources.Anthropic(self)
            # self.with_raw_response = OpenAIWithRawResponse(self)
            # self.with_streaming_response = OpenAIWithStreamedResponse(self)
            # from anthropic import Anthropic
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "Please install the `anthropic` package to use the Anthropic resources, you can install it by `pip install anthropic`"
                )
            self._anthropic: anthropic.Anthropic | None = None
            self._anthropic_params = {
                "api_key": self.api_key,
                "base_url": self.config.base_url,  # type: ignore[call-arg]
                "timeout": self.config.timeout,  # type: ignore[call-arg]
                "max_retries": self.config.max_retries,  # type: ignore[call-arg]
                "http_client": self.config.http_client,  # type: ignore[call-arg]
                "default_headers": self.config.default_headers,
                "default_query": self.config.default_query,
                "_strict_response_validation": self.config._strict_response_validation,  # type: ignore[call-arg]
            }
                
    
    @property
    def anthropic(self):
        if self._anthropic is None:
            from anthropic import Anthropic
            self._anthropic = Anthropic(**self._anthropic_params)
        return self._anthropic
    
    @property
    def Stream(self):
        return Stream
    
    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }
    
    def stream_to_generator(self, stream_obj: "Stream") -> Generator:
        """make a stream object to a generator that fit to client stream decoder"""
        for x in stream_obj:
            # print(x)
            yield f"data: {json.dumps(x)}\n\n"

    def _make_status_error(self, err_msg: str, *, body: object, response: httpx.Response) -> HAPIStatusError:
        """
        Make an APIStatusError from an error message, response body, and response object.
        For example: 
            err_msg: str, "Error code: 401 - {'detail': 'API-KEY not provied, please provide API Key in the header by set `Authorization` header'}"
            body: dict, {'detail': 'API-KEY not provied, please provide API Key in the header by set `Authorization` header'}
            response: httpx.Response, <Response [401]>
        """
        return HAPIStatusError(err_msg, body=body, response=response)
        
        
        # return super()._make_status_error(err_msg, body=body, response=response)


class AsyncHClient(AsyncAPIClient):
    """
    高能AI框架基础异步客户端
    """
    NotGiven = NOT_GIVEN

    def __init__(
            self,
            config: HClientConfig = None,
            **overrides,  # 用于覆盖默认配置
    ):
        self.config = config or HClientConfig()
        if overrides:
            self.config.update_by_dict(overrides)
        
        api_key = self.config.api_key
        if api_key == NOT_GIVEN:  # 人为设置为NOT_GIVEN时，不报错
            pass
        elif api_key is None:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the environment variable"
            )
        self.api_key = api_key

        if self.config.base_url == NOT_GIVEN:
            self.config.base_url = httpx.URL("")
            pass
        elif self.config.base_url is None:
            raise ValueError(
                "The base_url client option must be set, you can set it by passing base_url to the client or by setting the environment variable"
            )
        
        if (self.config.proxy is not None) and (self.config.http_client is None):
            print(f'[AsyncHClient] Proxy: {self.config.proxy}')
            self.config.instantiate_http_client()  # 提前实例化http_client，就设置了proxy

        super().__init__(
            version=self.config.version,
            base_url=self.config.base_url,
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
            http_client=self.config.http_client,
            custom_headers=self.config.default_headers,
            custom_query=self.config.default_query,
            _strict_response_validation=self.config._strict_response_validation,
        )

        if self.config.enable_openai:
            """集成openai的resources"""
            from .openai_api import resources
            self.completions = resources.AsyncCompletions(self)
            self.chat = resources.AsyncChat(self)
            self.embeddings = resources.AsyncEmbeddings(self)
            self.files = resources.AsyncFiles(self)
            self.images = resources.AsyncImages(self)
            self.audio = resources.AsyncAudio(self)
            self.moderations = resources.AsyncModerations(self)
            self.models = resources.AsyncModels(self)
            self.fine_tuning = resources.AsyncFineTuning(self)
            self.beta = resources.AsyncBeta(self)
            self.batches = resources.AsyncBatches(self)
            self.uploads = resources.AsyncUploads(self)

    @property
    def Stream(self):
        # return Stream
        return AsyncStream
    
    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    async def stream_to_generator(self, stream_obj: "Stream") -> AsyncGenerator:
        """Make a stream object to an async generator that fits the client stream decoder"""
        async for x in stream_obj:
            yield f"data: {json.dumps(x)}\n\n"

    def _make_status_error(self, err_msg: str, *, body: object, response: httpx.Response) -> HAPIStatusError:
        """
        Make an APIStatusError from an error message, response body, and response object.
        """
        return HAPIStatusError(err_msg, body=body, response=response)



if __name__ == "__main__":
    client = HClient(base_url="http://localhost:42600/apiv2")    
    
    from hepai.components.haiddf.hclient.openai_api import Stream
    from typing import Any
    data_need_stream = [
            1, 2, 3,
            "x", "y", "z",
            [[1, 2], [3, 4], [5, 6]],
            {"a": "b", "c": "d"},
        ]
    
    rst = client.post(
            path="/worker_unified_gate/?function=get_stream", 
            cast_to=Any,
            body={"kwargs": {"data": data_need_stream, "interval": 0.1}},
            stream=True,
            stream_cls=Stream[Any],
            )
    for i, x in enumerate(rst):
        print(f"i: {i}, x: {x}, type: {type(x)}")