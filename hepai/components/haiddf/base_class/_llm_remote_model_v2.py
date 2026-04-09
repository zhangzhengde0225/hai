"""
LLMRemoteModel v2 —— 纯 httpx 实现。

与 v1 的主要差异：
- 完全移除对 OpenAI SDK 和 Anthropic SDK 的依赖，改用 httpx.AsyncClient 直接发送 HTTP 请求
- 非流式方法统一返回 dict（v1 返回 SDK 对象）
- 流式方法 yield 原始 SSE bytes（v1 yield str）
- rerank 改为异步实现

适配性更强，可对接任何符合 OpenAI/Anthropic HTTP 协议的模型平台。
"""

import os
import re
import json
from typing import Union, Dict, List, Optional, AsyncGenerator, Literal
from dataclasses import dataclass, field

import httpx

from ._worker_class import HRModel, HModelConfig


class LLMRemoteModelV2(HRModel):

    def __init__(self, config: "LLMModelConfig"):
        super().__init__(config=config)
        self.cfg = config
        self.engine = config.engine
        self._http_client: Optional[httpx.AsyncClient] = None
        self._anthropic_http_client: Optional[httpx.AsyncClient] = None

    # ── httpx 客户端（懒加载）────────────────────────────────────────────

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = self._build_async_client(self.cfg.base_url)
        return self._http_client

    @property
    def anthropic_http_client(self) -> httpx.AsyncClient:
        if self._anthropic_http_client is None:
            self._anthropic_http_client = self._build_async_client(
                self._resolve_anthropic_base_url()
            )
        return self._anthropic_http_client

    def _build_async_client(self, base_url: str) -> httpx.AsyncClient:
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        timeout = httpx.Timeout(timeout=600.0, connect=10.0)
        kwargs: Dict = dict(
            base_url=base_url,
            timeout=timeout,
            limits=limits,
            follow_redirects=True,
        )
        if self.cfg.proxy:
            kwargs["proxy"] = self.cfg.proxy
        return httpx.AsyncClient(**kwargs)

    # ── URL 解析 ─────────────────────────────────────────────────────────

    def _build_oai_url(self, path: str) -> str:
        """在 base_url 后拼接路径，确保有版本号前缀。"""
        base = self.cfg.base_url.rstrip("/")
        if not re.search(r"/v\d+$", base):
            base = f"{base}/v1"
        return f"{base}{path}"

    def _resolve_anthropic_base_url(self) -> str:
        """
        复刻 v1 async_client_with_anthropic_url 的逻辑：
        去掉末尾 /vN，添加 /anthropic 后缀。
        """
        base = self.cfg.base_url
        if re.search(r"/v\d+$", base):
            base = base.rsplit("/", 1)[0]
        base = base.rstrip("/")
        if not base.endswith("/anthropic"):
            base = base + "/anthropic"
        return base

    def _build_anthropic_url(self, path: str) -> str:
        """Anthropic 接口完整 URL，如 /v1/messages。"""
        return self._resolve_anthropic_base_url().rstrip("/") + path

    # ── 属性 ─────────────────────────────────────────────────────────────

    @property
    def is_o1(self) -> bool:
        m = self.engine.split("/")[1] if "/" in self.engine else self.engine
        return m in ["o1", "o1-mini", "o1-preview"]

    def __repr__(self):
        return f"<LLMRemoteModelV2 name={self.cfg.name} engine={self.cfg.engine}>"

    # ── 内部工具 ─────────────────────────────────────────────────────────

    @staticmethod
    def _make_exception(kwargs, payload, url, resp, error_text: str = None) -> Exception:
        actual_text = error_text if error_text is not None else resp.text
        error_msg = f"Upstream Responses Error {resp.status_code}: {actual_text}"
        exc = Exception(error_msg)
        exc.add_note(f"请求目标 URL: {url}")
        exc.add_note(f"传递的模型: {payload.get('model') or kwargs.get('model')}")
        exc.add_note(f"请求 Payload (前300字符): {str(payload)[:300]}")
        return exc

    @staticmethod
    def _filter_none(d: dict) -> dict:
        """过滤掉值为 None 的顶层 key。"""
        return {k: v for k, v in d.items() if v is not None}

    def _resolve_oai_auth_headers(self, kwargs: dict) -> dict:
        """提取 Authorization 头，同时从 kwargs 中 pop 掉 api_key / extra_headers。"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
            return {"Authorization": f"Bearer {api_key}"}
        else:
            kwargs.pop("api_key", None)
            return kwargs.pop("extra_headers", {}) or {}

    def _resolve_anthropic_auth_headers(self, kwargs: dict) -> dict:
        """提取 Anthropic 鉴权头（x-api-key），同时 pop 相关参数。"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
            headers = {"x-api-key": api_key}
        else:
            kwargs.pop("api_key", None)
            headers = dict(kwargs.pop("extra_headers", {}) or {})

        anthropic_version = kwargs.pop("anthropic_version", None)
        anthropic_beta = kwargs.pop("anthropic_beta", None)
        headers.setdefault("anthropic-version", "2023-06-01")
        if anthropic_version:
            headers["anthropic-version"] = anthropic_version
        if anthropic_beta:
            headers["anthropic-beta"] = anthropic_beta
        return headers

    # ── 通用流式字节生成器 ────────────────────────────────────────────────

    async def _stream_bytes(self, client: httpx.AsyncClient, url: str,
                            headers: dict, payload: dict,
                            timeout: float) -> AsyncGenerator[bytes, None]:
        """向 url 发送流式 POST，透传原始 SSE 字节，带内联 JSON 错误检测。"""
        async with client.stream("POST", url, headers=headers,
                                 json=payload, timeout=timeout) as resp:
            if resp.status_code != 200:
                await resp.aread()
                raise self._make_exception({}, payload, url, resp)

            is_first = True
            is_error = False
            error_buf = bytearray()

            async for chunk in resp.aiter_bytes():
                if is_first:
                    is_first = False
                    if chunk.lstrip().startswith(b"{"):
                        is_error = True
                if is_error:
                    error_buf.extend(chunk)
                else:
                    yield chunk

            if is_error:
                full = error_buf.decode("utf-8", errors="ignore")
                raise self._make_exception({}, payload, url, resp, error_text=full)

    @staticmethod
    async def _sse_bytes_to_dicts(stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[dict, None]:
        """
        将 SSE 字节流解析为 dict 生成器。
        供 general.convert_openai_to_anthropic_format_stream 使用（该函数接受 dict 迭代器）。
        """
        buf = b""
        async for chunk in stream:
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if line.startswith(b"data:"):
                    data_str = line[5:].strip()
                    if data_str and data_str != b"[DONE]":
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            pass

    # ── 对外方法 ──────────────────────────────────────────────────────────

    @HRModel.remote_callable
    async def chat_completions(self, *args, **kwargs):
        """OpenAI Chat Completions 接口（/v1/chat/completions）。

        非流式返回 dict；流式返回 AsyncGenerator[bytes]，每个 chunk 为原始 SSE 字节。
        """
        extra_headers = self._resolve_oai_auth_headers(kwargs)

        chat_messages = kwargs.pop("messages")
        assert chat_messages, "messages is required"
        kwargs.pop("model", None)
        should_stream = kwargs.pop("stream", False)

        # if self.is_o1:
        #     kwargs.pop("temperature", None)
        #     kwargs.pop("top_p", None)

        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        timeout = kwargs.pop("timeout", None) or 600.0
        kwargs.pop("not_stream_to_str", None)

        stream_options = kwargs.pop("stream_options", {}) or {}
        if should_stream:
            stream_options["include_usage"] = True

        payload: dict = {
            "model": self.engine,
            "messages": chat_messages,
            "stream": should_stream,
        }
        if should_stream and stream_options:
            payload["stream_options"] = stream_options
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        payload.update(extra_body)

        url = self._build_oai_url("/chat/completions")
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.cfg.api_key}" if self.cfg.api_key else None,
            **extra_headers}

        if should_stream:
            return self._stream_bytes(self.http_client, url, headers, payload, timeout)
        else:
            resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code != 200:
                raise self._make_exception(kwargs, payload, url, resp)
            return resp.json()

    @HRModel.remote_callable
    async def responses(self, *args, **kwargs):
        """处理 /v1/responses 接口（与 v1 逻辑相同，改用持久 http_client）。"""
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            api_key = kwargs.pop("api_key", None) or self.cfg.api_key
            extra_headers = {"Authorization": f"Bearer {api_key}"}
            extra_headers.update(kwargs.pop("extra_headers", {}) or {})

        kwargs.pop("extra_body", None)
        kwargs.pop("extra_query", None)
        kwargs.pop("stream_options", None)
        timeout = kwargs.pop("timeout", 60.0) or 60.0

        kwargs["model"] = self.cfg.engine
        stream = kwargs.get("stream", False)
        payload = dict(kwargs)

        base_url = self.cfg.base_url.rstrip("/")
        if re.search(r"/v\d+$", base_url):
            url = f"{base_url}/responses"
        else:
            url = f"{base_url}/v1/responses"

        if stream:
            return self._stream_bytes(self.http_client, url, extra_headers, payload, timeout)
        else:
            resp = await self.http_client.post(url, headers=extra_headers, json=payload, timeout=timeout)
            if resp.status_code != 200:
                raise self._make_exception(kwargs, payload, url, resp)
            return resp.json()

    @HRModel.remote_callable
    async def embeddings(self, *args, **kwargs):
        """OpenAI Embeddings 接口（/v1/embeddings）。"""
        extra_headers = self._resolve_oai_auth_headers(kwargs)
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        kwargs.pop("stream", None)
        kwargs.pop("model", None)
        timeout = kwargs.pop("timeout", None) or 120.0
        input_data = kwargs.pop("input", None)

        payload: dict = self._filter_none({
            "model": self.engine,
            "input": input_data,
            **kwargs,
            **extra_body,
        })

        url = self._build_oai_url("/embeddings")
        headers = {"Content-Type": "application/json", **extra_headers}
        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    async def rerank(self, *args, **kwargs):
        """Rerank 接口（异步实现，移除了 v1 中的同步 httpx.Client）。"""
        extra_headers = self._resolve_oai_auth_headers(kwargs)
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        kwargs.pop("stream", None)
        timeout = kwargs.pop("timeout", None) or 120.0

        query = kwargs.pop("query", None)
        kwargs.pop("model", None)
        top_n = kwargs.pop("top_n", 3)
        documents = kwargs.pop("documents", None)
        return_documents = kwargs.pop("return_documents", False)

        payload: dict = {
            "model": self.engine,
            "query": query,
            "top_n": top_n,
            "documents": documents,
            "return_documents": return_documents,
            **extra_body,
        }

        base_url = self.cfg.base_url.rstrip("/")
        if re.search(r"/v\d+$", base_url):
            url = f"{base_url}/rerank"
        else:
            url = f"{base_url}/v1/rerank"

        headers = {"Content-Type": "application/json", **extra_headers}
        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @HRModel.remote_callable
    async def image_generations(self, *args, **kwargs):
        """OpenAI Images Generations 接口（/v1/images/generations）。"""
        extra_headers = self._resolve_oai_auth_headers(kwargs)
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        kwargs.pop("stream", None)
        kwargs.pop("model", None)
        timeout = kwargs.pop("timeout", None) or 120.0
        prompt = kwargs.pop("prompt", None)

        payload: dict = self._filter_none({
            "model": self.engine,
            "prompt": prompt,
            **kwargs,
            **extra_body,
        })

        url = self._build_oai_url("/images/generations")
        headers = {"Content-Type": "application/json", **extra_headers}
        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    async def anthropic_messages(self, *args, **kwargs) -> Union[Dict, AsyncGenerator]:
        """Anthropic Messages API（/v1/messages）。

        非流式返回 dict；流式返回 AsyncGenerator[bytes]，原始 SSE 字节。
        moonshot/openai/kimi/gpt 模型自动路由到 chat_completions 并做格式转换。
        """
        modelx = kwargs.get("model", "")
        stream = kwargs.get("stream", False)

        # 非 Claude 模型：路由到 OAI 接口并转换格式
        if any(x in modelx.lower() for x in ["moonshot", "openai", "kimi", "gpt"]):
            from . import general
            oai_params = await general.convert_input_anthropic_to_openai_format(kwargs)
            if stream:
                oai_params["stream"] = True
                bytes_stream = await self.chat_completions(**oai_params)
                dict_stream = self._sse_bytes_to_dicts(bytes_stream)
                gen = general.convert_openai_to_anthropic_format_stream(dict_stream, return_dict=False)
                return gen
            else:
                rst_dict = await self.chat_completions(**oai_params)
                # 使用纯 dict 版本的转换函数（v1 的 convert_object_openai_to_anthropic 需要 SDK 对象）
                rst2 = await general.convert_openai_to_anthropic_format(rst_dict)
                return rst2

        # Claude 模型：直接调用 Anthropic HTTP 接口
        extra_headers = self._resolve_anthropic_auth_headers(kwargs)
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        timeout = kwargs.pop("timeout", None) or 600.0

        if "model" not in kwargs:
            raise ValueError("model parameter is required")
        if "messages" not in kwargs:
            raise ValueError("messages parameter is required")
        if "max_tokens" not in kwargs:
            raise ValueError("max_tokens parameter is required")

        kwargs.pop("model")
        messages = kwargs.pop("messages")
        max_tokens = kwargs.pop("max_tokens")

        # thinking / reasoning 参数处理（与 v1 完全一致）
        thinking = kwargs.pop("thinking", {}) or {}
        reasoning = kwargs.pop("reasoning", {}) or {}
        assert not (thinking and reasoning), "thinking and reasoning parameters cannot exist at the same time"
        if thinking:
            if thinking.get("type") == "enabled":
                budget_tokens = thinking.get("budget_tokens", 0)
                max_tokens = max(max_tokens, budget_tokens + 1)
        elif reasoning:
            enabled = reasoning.get("enabled", False)
            if enabled:
                budget_tokens = max_tokens - 1
                thinking = {"type": "enabled", "budget_tokens": budget_tokens}
            else:
                effort = reasoning.get("effort", "low")
                if str(effort) in ["None", "minimal", "low"]:
                    thinking = {"type": "disabled"}
                elif str(effort) in ["medium", "high", "xhigh"]:
                    thinking = {"type": "adaptive"}
                else:
                    raise ValueError(f"Invalid reasoning effort level: {effort}")

        stream = kwargs.pop("stream", False)
        kwargs.pop("context_management", None)
        kwargs.pop("store", None)

        payload: dict = {
            "model": self.engine,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if thinking:
            payload["thinking"] = thinking
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        payload.update(extra_body)

        url = self._build_anthropic_url("/v1/messages")
        headers = {"Content-Type": "application/json", **extra_headers}

        if stream:
            return self._stream_bytes(self.anthropic_http_client, url, headers, payload, timeout)
        else:
            resp = await self.anthropic_http_client.post(
                url, headers=headers, json=payload, timeout=timeout
            )
            if resp.status_code != 200:
                raise self._make_exception(kwargs, payload, url, resp)
            data = resp.json()
            if data.get("type") == "error":
                raise ValueError(f"Anthropic API Error: {data.get('error', {})}")
            return data

    @HRModel.remote_callable
    async def anthropic_count_tokens(self, *args, **kwargs) -> Dict:
        """Anthropic Count Tokens 接口（/v1/messages/count_tokens）。"""
        extra_headers = self._resolve_anthropic_auth_headers(kwargs)
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        timeout = kwargs.pop("timeout", None) or 120.0

        if "model" not in kwargs:
            raise ValueError("model parameter is required")
        if "messages" not in kwargs:
            raise ValueError("messages parameter is required")

        kwargs.pop("model")
        messages = kwargs.pop("messages")

        payload: dict = {
            "model": self.engine,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if v is not None},
            **extra_body,
        }

        url = self._build_anthropic_url("/v1/messages/count_tokens")
        headers = {"Content-Type": "application/json", **extra_headers}
        resp = await self.anthropic_http_client.post(
            url, headers=headers, json=payload, timeout=timeout
        )
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    def custom_method(self, a: int, b: int) -> int:
        """示例自定义方法。"""
        return a + b

    @staticmethod
    def from_config(config_path: str) -> List["LLMRemoteModelV2"]:
        """从 worker_config.json 文件批量实例化模型对象。

        支持格式：
        {
          "models": {
            "providers": {
              "<provider>": {
                "baseUrl": "...",
                "apiKey": "...",
                "models": [ {"id": "...", "engine": "...", ...}, ... ]
              }
            }
          }
        }
        """
        with open(config_path, "r", encoding="utf-8") as f:
            cfg: Dict = json.load(f)


        meta = cfg.get("meta", {})
        version = meta.get("version", "2.0")

        providers = cfg.get("models", {}).get("providers", {})
        models: List["LLMRemoteModelV2"] = []
        for provider_name, provider in providers.items():
            base_url = provider.get("baseUrl", "")
            api_key = provider.get("apiKey", "")
            need_external = provider.get("needExternalApiKey", False)
            proxy = provider.get("proxy", None)
            api_mode = provider.get("api", "openai-completions")

            for m in provider.get("models", []):
                model_id = m.get("id") or m.get("name")
                engine = m.get("engine") or model_id
                name = m.get("name") or model_id
                proxy = m.get("proxy", proxy)  # 模型级 proxy 优先于 provider 级 proxy
                api_mode = m.get("api", api_mode)  # 模型级 api 模式 优先于 provider 级 api 模式
                model_cfg = LLMModelConfig(
                    name=name,
                    engine=engine,
                    base_url=base_url,
                    _api_key=api_key,
                    provider=provider_name,
                    api_mode=api_mode,
                    proxy=proxy,
                    version=version,
                    need_external_api_key=need_external,
                )
                models.append(LLMRemoteModelV2(config=model_cfg))
        return models

    def get_models_from_config(self) -> List["LLMRemoteModelV2"]:
        """从配置批量实例化模型对象。"""
        supported_models = ["gpt-4o", "gpt-4o-mini", "claude-3-sonnet", "claude-3-haiku"]
        return [
            LLMRemoteModelV2(config=LLMModelConfig(
                name=m,
                engine=m,
                base_url=self.cfg.base_url,
                _api_key=self.cfg.api_key,
                proxy=self.cfg.proxy,
                version=self.cfg.version,
                need_external_api_key=self.cfg.need_external_api_key,
            ))
            for m in supported_models
        ]


@dataclass
class LLMModelConfig(HModelConfig):
    config_file: str = field(default=None, metadata={"help": "Model's config file path"})
    name: str = field(default="anthropic/claude-sonnet-4.6", metadata={"help": "Model's name"})
    engine: str = field(default="claude-sonnet-4.6", metadata={"help": "Model engine"})
    base_url: str = field(default="https://api.zhizengzeng.com/v1", metadata={"help": "Base url"})
    _api_key: str = field(default="os.environ/ZHIZENGZENG_API_KEY", metadata={"help": "API key"})
    provider: str = field(default=None, metadata={"help": "Model provider, e.g. openai, anthropic"})
    api_mode: Literal["openai-completions", "openai-responses", "anthropic-messages", "google-gemini"] = field(
        default="openai-completions", metadata={"help": "API mode to determine request format and endpoint"}
        )
    proxy: str = field(default=None, metadata={"help": "Proxy"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    need_external_api_key: bool = field(default=False, metadata={"help": "Need external api key"})
    enable_async: bool = field(default=True, metadata={"help": "Use async client"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission"})
    test: bool = field(default=False, metadata={"help": "Test model"})

    def __post_init__(self):
        if isinstance(self._api_key, str) and self._api_key.startswith("os.environ/"):
            environ_name = self._api_key.split("/")[1]
            self._api_key = os.getenv(environ_name)

    @property
    def api_key(self):
        return self._api_key
