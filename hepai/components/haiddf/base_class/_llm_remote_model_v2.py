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

    # 参与 JSON 持久化的字段名（排除 worker_name/model_config_dir/secret_key 等运行时字段）
    _JSON_FIELDS: set = {
        "host", "port", "auto_start_port", "controller_address", "route_prefix",
        "no_register", "permissions", "description", "daemon",
        "limit_model_concurrency", "enable_secret_key", "enable_llm_router",
        "is_free", "debug","priority","weight"
    }

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
        max_conc = getattr(self.cfg, "limit_model_concurrency", 4096) or 4096
        limits = httpx.Limits(
            max_connections=max_conc,
            max_keepalive_connections=max(max_conc // 2, 256),
            )
        # limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
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
        构建 anthropic-messages 请求的 base URL。
        若 cfg.anthropic_url 非空，使用它；否则回落到 cfg.base_url。
        """
        if self.cfg.anthropic_url:
            return self.cfg.anthropic_url.rstrip("/")
        return self.cfg.base_url.rstrip("/")

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
        # 如果actual_text过长，截取前300字符以免日志过大
        if len(actual_text) > 300:
            actual_text = actual_text[:300] + "..."
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

    # ─────────────────────────────────────────────────────────────────────
    # Anthropic 请求规整层（多客户端兼容）
    #
    # 抹平 Claude Code / OpenCode / cline / anthropic-sdk 等客户端在协议
    # 细节上的差异，保证上游（Anthropic 官方或智增增等中转商）能接受。
    # 新增字段兼容时只动这一段；anthropic_messages / anthropic_count_tokens
    # 函数本身不用关心这些细节。
    # ─────────────────────────────────────────────────────────────────────

    # Anthropic 内置工具的 type 前缀，原样透传不做 OpenAI→Anthropic 转换
    _ANTHROPIC_BUILTIN_TOOL_PREFIXES = (
        "bash_", "text_editor_", "computer_", "code_execution_", "memory_",
        "web_search_", "file_search_",
    )

    # 上游 Anthropic Messages 接口不接受、必须在转发前 drop 的字段
    _ANTHROPIC_INCOMPATIBLE_FIELDS = (
        "context_management",     # Claude Code 2.0.62+ 自动对话压缩（beta）
        "store",                  # 服务端记忆（beta）
        "stream_options",         # OpenAI 客户端流式自动附加
        "max_completion_tokens",  # OpenAI 字段（Anthropic 用 max_tokens）
        "output_config",          # Anthropic Opus 4.6+ 新字段（effort/task_budget/format），需要
                                  # task-budgets-2026-03-13 等 beta header；多数中转商不支持，
                                  # 解析时会让整个 body 失败（症状：上游报 "Missing 'model'"）
    )

    @staticmethod
    def _strip_thinking_blocks(messages: list) -> list:
        """剥离历史 assistant 中的 thinking / redacted_thinking content block。

        extended thinking 返回的 thinking block 带 signature 字段，回传时会被
        服务端验证；signature 与生成它的上游账号绑定，跨中转商必失败。这里统一
        剥离历史 thinking，副作用是 Claude 看不到上几轮"内心思考"，text 输出
        仍保留——实测对回答质量影响极小。
        """
        cleaned = []
        for msg in messages:
            if not isinstance(msg, dict) or msg.get("role") != "assistant":
                cleaned.append(msg)
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                cleaned.append(msg)
                continue
            new_content = [
                c for c in content
                if not (isinstance(c, dict) and c.get("type") in ("thinking", "redacted_thinking"))
            ]
            if not new_content:
                # 剥离后内容为空就跳过整条 assistant 消息（Anthropic 不接受空 content）
                continue
            new_msg = dict(msg)
            new_msg["content"] = new_content
            cleaned.append(new_msg)
        return cleaned

    @staticmethod
    def _extract_system_from_messages(messages: list, current_system):
        """把 messages 中 role=system 的条目抽出来合并到顶级 system 字段。

        OpenAI 风格客户端常把 system prompt 塞到 messages[0]，但 Anthropic 要求
        system 走顶级字段，messages 里只允许 user/assistant。返回
        (cleaned_messages, system_value)；若顶级 system 已存在则把消息中的
        system 文本拼到其前面。
        """
        sys_parts: list = []
        cleaned: list = []
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "system":
                content = msg.get("content")
                if isinstance(content, str):
                    sys_parts.append(content)
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text" and isinstance(c.get("text"), str):
                            sys_parts.append(c["text"])
                        elif isinstance(c, str):
                            sys_parts.append(c)
                continue
            cleaned.append(msg)
        if not sys_parts:
            return cleaned, current_system
        sys_from_msgs = "\n\n".join(sys_parts)
        if current_system in (None, ""):
            return cleaned, sys_from_msgs
        if isinstance(current_system, str):
            return cleaned, f"{sys_from_msgs}\n\n{current_system}"
        if isinstance(current_system, list):
            return cleaned, [{"type": "text", "text": sys_from_msgs}] + current_system
        return cleaned, current_system

    @staticmethod
    def _sanitize_messages(messages: list) -> list:
        """收尾清洗 messages：移除顶层 cache_control + 去掉相邻重复消息。

        - 顶层 cache_control 是 OpenAI 风格客户端的常见错放（Anthropic 要求在
          content block 内）。直接 drop。
        - 客户端 bug 偶尔重发相同消息，Anthropic 拒绝同 role 连续——这里仅合并
          "相邻且 content 完全一致"的同 role 消息（保守去重）。
        """
        cleaned = []
        for msg in messages:
            if not isinstance(msg, dict):
                cleaned.append(msg)
                continue
            new_msg = {k: v for k, v in msg.items() if k != "cache_control"}
            if cleaned and isinstance(cleaned[-1], dict):
                prev = cleaned[-1]
                if (
                    prev.get("role") == new_msg.get("role")
                    and prev.get("content") == new_msg.get("content")
                ):
                    continue
            cleaned.append(new_msg)
        return cleaned

    @staticmethod
    def _normalize_tool_choice(tool_choice):
        """OpenAI 风格 tool_choice → Anthropic 风格 object。

        OpenAI: "auto" / "none" / "required" 字符串，或 {"type":"function","function":{"name":"X"}}
        Anthropic: {"type":"auto"} / {"type":"any"} / {"type":"tool","name":"X"}（无 "none"）
        返回 None 表示该字段应当从 payload 中移除。
        """
        if tool_choice is None:
            return None
        if isinstance(tool_choice, dict):
            if "function" in tool_choice and isinstance(tool_choice["function"], dict):
                name = tool_choice["function"].get("name")
                return {"type": "tool", "name": name} if name else {"type": "auto"}
            return tool_choice
        if isinstance(tool_choice, str):
            return {
                "auto": {"type": "auto"},
                "required": {"type": "any"},
                "any": {"type": "any"},
                "none": None,
            }.get(tool_choice, {"type": "auto"})
        return tool_choice

    @classmethod
    def _normalize_tools(cls, tools):
        """OpenAI 风格 tools → Anthropic 风格自定义工具；内置工具原样保留。

        OpenAI:    {"type":"function","function":{"name":...,"description":...,"parameters":{...}}}
        Anthropic: {"name":...,"description":...,"input_schema":{...}}
        """
        if not isinstance(tools, list):
            return tools
        converted = []
        for t in tools:
            if not isinstance(t, dict):
                converted.append(t)
                continue
            t_type = t.get("type")
            if isinstance(t_type, str) and t_type.startswith(cls._ANTHROPIC_BUILTIN_TOOL_PREFIXES):
                converted.append(t)
                continue
            if t_type == "function" and isinstance(t.get("function"), dict):
                fn = t["function"]
                converted.append({
                    "name": fn.get("name"),
                    "description": fn.get("description", ""),
                    "input_schema": fn.get("parameters") or {"type": "object", "properties": {}},
                })
                continue
            converted.append(t)
        return converted

    # ─────────────────────────────────────────────────────────────────────
    # OpenAI Responses 请求规整层
    # 同样针对跨上游兼容；目前主要是剥离 encrypted_content（reasoning 加密内容）。
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _strip_responses_encrypted_content(input_value):
        """剥离 Responses input 中的 reasoning 项与 encrypted_content 字段。

        gpt-5 系列模型返回的 output 中会带 type=reasoning 项以及各 content 块上
        的 encrypted_content（服务端加密 token）。Codex 等客户端会把这些原样回传
        给下一轮请求，跨上游账号必然解不开（"encrypted content could not be
        verified"）。这里在转发前统一剥离，等同于 anthropic thinking signature
        的兜底——副作用是历史 reasoning 上下文丢失，但 message 文本输出仍保留。
        """
        if not isinstance(input_value, list):
            return input_value
        cleaned = []
        for item in input_value:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            # 整条 drop 历史 reasoning 项
            if item.get("type") == "reasoning":
                continue
            new_item = {k: v for k, v in item.items() if k != "encrypted_content"}
            content = new_item.get("content")
            if isinstance(content, list):
                new_content = []
                for c in content:
                    if isinstance(c, dict):
                        new_content.append({k: v for k, v in c.items() if k != "encrypted_content"})
                    else:
                        new_content.append(c)
                new_item["content"] = new_content
            cleaned.append(new_item)
        return cleaned

    @classmethod
    def _normalize_responses_request(cls, kwargs: dict) -> dict:
        """统一规整 responses() 的 kwargs（原地修改并返回）。

        当前处理：剥离 input 中跨上游解不开的 encrypted_content。
        新增 OpenAI 客户端兼容项时扩展本方法。
        """
        if "input" in kwargs:
            kwargs["input"] = cls._strip_responses_encrypted_content(kwargs["input"])
        # include 字段若申请返回加密内容会污染下一轮，过滤掉
        include = kwargs.get("include")
        if isinstance(include, list):
            include = [x for x in include if x != "reasoning.encrypted_content"]
            if include:
                kwargs["include"] = include
            else:
                kwargs.pop("include", None)
        return kwargs

    @staticmethod
    def _resolve_thinking(kwargs: dict, max_tokens: int):
        """解析 thinking / reasoning 参数，返回 (thinking_dict, max_tokens)。

        - thinking 直接透传给 Anthropic；budget_tokens 触发 max_tokens 上浮。
        - reasoning 是 OpenAI / 通用风格，按 effort 映射到 anthropic thinking。
        - 两者不可同时存在。
        """
        thinking = kwargs.pop("thinking", {}) or {}
        reasoning = kwargs.pop("reasoning", {}) or {}
        assert not (thinking and reasoning), "thinking 和 reasoning 不能同时存在"
        if thinking:
            if thinking.get("type") == "enabled":
                budget_tokens = thinking.get("budget_tokens", 0)
                max_tokens = max(max_tokens, budget_tokens + 1)
        elif reasoning:
            enabled = reasoning.get("enabled", False)
            if enabled:
                thinking = {"type": "enabled", "budget_tokens": max_tokens - 1}
            else:
                effort = str(reasoning.get("effort", "low"))
                if effort in ("None", "minimal", "low"):
                    thinking = {"type": "disabled"}
                elif effort in ("medium", "high", "xhigh"):
                    thinking = {"type": "adaptive"}
                else:
                    raise ValueError(f"Invalid reasoning effort level: {effort}")
        return thinking, max_tokens

    @classmethod
    def _normalize_anthropic_request(cls, kwargs: dict) -> dict:
        """统一规整 anthropic_messages / anthropic_count_tokens 的 kwargs。

        兼容客户端：Claude Code、OpenCode、cline、anthropic-sdk 等。
        新增兼容项时只动这一段。kwargs 被原地修改并返回，便于链式书写。

        处理项：
          messages —— 剥离历史 thinking、抽 system 到顶级、移除顶层 cache_control、去重相邻重复
          tools    —— OpenAI function-style → Anthropic 自定义工具；内置工具原样保留
          tool_choice —— 字符串 / OpenAI function 形态 → Anthropic object（"none" 直接删字段）
          字段过滤 —— drop _ANTHROPIC_INCOMPATIBLE_FIELDS 中列出的字段
        """
        # messages
        if "messages" in kwargs:
            messages = kwargs["messages"]
            messages = cls._strip_thinking_blocks(messages)
            messages, system = cls._extract_system_from_messages(messages, kwargs.get("system"))
            if system in (None, ""):
                kwargs.pop("system", None)
            else:
                kwargs["system"] = system
            kwargs["messages"] = cls._sanitize_messages(messages)

        # tool_choice
        if "tool_choice" in kwargs:
            tc = cls._normalize_tool_choice(kwargs["tool_choice"])
            if tc is None:
                kwargs.pop("tool_choice", None)
            else:
                kwargs["tool_choice"] = tc

        # tools
        if kwargs.get("tools"):
            kwargs["tools"] = cls._normalize_tools(kwargs["tools"])

        # 上游不兼容字段
        for k in cls._ANTHROPIC_INCOMPATIBLE_FIELDS:
            kwargs.pop(k, None)

        return kwargs

    def _build_oai_headers(self, kwargs: dict) -> dict:
        """构建 OpenAI 风格请求的完整 headers，封装 API key。

        - need_external_api_key=True：从 kwargs 强制取 api_key
        - need_external_api_key=False：使用 self.cfg.api_key；合并调用方的 extra_headers
        """
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
        else:
            api_key = kwargs.pop("api_key", None) or self.cfg.api_key
        caller_extra = kwargs.pop("extra_headers", {}) or {}
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        headers.update(caller_extra)
        return headers

    def _build_anthropic_headers(self, kwargs: dict) -> dict:
        """构建 Anthropic 风格请求的完整 headers，封装 API key 及版本头。

        - need_external_api_key=True：从 kwargs 强制取 api_key
        - need_external_api_key=False：使用 self.cfg.api_key；合并调用方的 extra_headers
        """
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provide API-KEY when calling this worker")
        else:
            api_key = kwargs.pop("api_key", None) or self.cfg.api_key
        caller_extra = dict(kwargs.pop("extra_headers", {}) or {})
        anthropic_version = kwargs.pop("anthropic_version", None)
        anthropic_beta = kwargs.pop("anthropic_beta", None)
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key
        if anthropic_version:
            headers["anthropic-version"] = anthropic_version
        else:
            headers.setdefault("anthropic-version", "2023-06-01")
        if anthropic_beta:
            headers["anthropic-beta"] = anthropic_beta
        headers.update(caller_extra)
        return headers

    # ── 通用流式字节生成器 ────────────────────────────────────────────────

    @staticmethod
    def _format_sse_error_bytes(status_code: int, error_text: str, url: str, model: str) -> bytes:
        """构造一个标准 SSE 错误事件，让客户端 SDK 能解析到具体错误。

        流式响应 HTTP 200 头已经发出后，再 raise Exception 会让 starlette 截断流，
        客户端只能看到模糊的"stream interrupted"。改为 yield 这个 SSE 错误事件，
        OpenAI / Anthropic 风格客户端都能识别出错误细节。
        """
        # 截断超长 error_text 避免日志/响应过大
        truncated = error_text if len(error_text) <= 1500 else error_text[:1500] + "...[truncated]"
        payload = {
            "type": "error",
            "error": {
                "type": "upstream_error",
                "code": status_code,
                "message": truncated,
                "upstream_url": url,
                "model": model,
            },
        }
        return f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")

    async def _stream_bytes(self, client: httpx.AsyncClient, url: str,
                            headers: dict, payload: dict,
                            timeout: float) -> AsyncGenerator[bytes, None]:
        """向 url 发送流式 POST，透传原始 SSE 字节，带内联 JSON 错误检测。

        中途出错时不 raise（HTTP 200 头已发，starlette 无法回滚状态码），改为
        yield 一个 SSE 错误事件，并把详细信息写入 logger 供运维排查。
        """
        model = payload.get("model", "-")
        try:
            async with client.stream("POST", url, headers=headers,
                                     json=payload, timeout=timeout) as resp:
                if resp.status_code != 200:
                    await resp.aread()
                    exc = self._make_exception({}, payload, url, resp)
                    self._log_stream_error(exc)
                    yield self._format_sse_error_bytes(
                        resp.status_code, resp.text, url, model
                    )
                    return

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
                    exc = self._make_exception({}, payload, url, resp, error_text=full)
                    self._log_stream_error(exc)
                    yield self._format_sse_error_bytes(resp.status_code, full, url, model)
                    return
        except Exception as e:
            # 网络异常 / timeout / SSL 等：上游未必有 status_code，照样兜底
            self._log_stream_error(e)
            yield self._format_sse_error_bytes(
                getattr(e, "status_code", 0) or 0,
                f"{type(e).__name__}: {e}",
                url, model,
            )

    def _log_stream_error(self, exc: Exception):
        """把流式出错的详细信息写入 logger（保留 add_note 信息）。"""
        try:
            logger = getattr(self, "logger", None)
            msg = f"[_stream_bytes] {type(exc).__name__}: {exc}"
            notes = getattr(exc, "__notes__", None)
            if notes:
                msg += "\n" + "\n".join(notes)
            if logger:
                logger.error(msg)
            else:
                # 没接 logger 也要让信息进 stderr 不至于丢
                import sys as _sys
                print(msg, file=_sys.stderr)
        except Exception:
            pass

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
        headers = self._build_oai_headers(kwargs)

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

        if should_stream:
            return self._stream_bytes(self.http_client, url, headers, payload, timeout)
        else:
            resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code != 200:
                raise self._make_exception(kwargs, payload, url, resp)
            return resp.json()

    @HRModel.remote_callable
    async def responses(self, *args, **kwargs):
        """处理 /v1/responses 接口（与 v1 逻辑相同，改用持久 http_client）。

        支持 Codex / openai-sdk / OpenCode 等客户端；跨上游兼容由
        _normalize_responses_request 处理（剥离跨账号解不开的 encrypted_content）。
        """
        headers = self._build_oai_headers(kwargs)

        kwargs.pop("extra_body", None)
        kwargs.pop("extra_query", None)
        kwargs.pop("stream_options", None)
        timeout = kwargs.pop("timeout", 60.0) or 60.0

        # 跨客户端兼容规整
        self._normalize_responses_request(kwargs)

        kwargs["model"] = self.cfg.engine
        stream = kwargs.get("stream", False)
        payload = dict(kwargs)

        base_url = self.cfg.base_url.rstrip("/")
        if re.search(r"/v\d+$", base_url):
            url = f"{base_url}/responses"
        else:
            url = f"{base_url}/v1/responses"

        if stream:
            return self._stream_bytes(self.http_client, url, headers, payload, timeout)
        else:
            resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code != 200:
                raise self._make_exception(kwargs, payload, url, resp)
            return resp.json()

    @HRModel.remote_callable
    async def responses_compact(self, *args, **kwargs):
        """OpenAI Responses Compact 接口（/v1/responses/compact）。

        对话压缩：将历史 response 压缩为更紧凑的形式，节省 token。
        请求体：response_id (必填), model (可选), input (可选)
        """
        headers = self._build_oai_headers(kwargs)
        kwargs.pop("extra_body", None)
        kwargs.pop("extra_query", None)
        timeout = kwargs.pop("timeout", 60.0) or 60.0

        kwargs["model"] = self.cfg.engine
        payload = dict(kwargs)

        base_url = self.cfg.base_url.rstrip("/")
        if re.search(r"/v\d+$", base_url):
            url = f"{base_url}/responses/compact"
        else:
            url = f"{base_url}/v1/responses/compact"

        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    async def embeddings(self, *args, **kwargs):
        """OpenAI Embeddings 接口（/v1/embeddings）。"""
        headers = self._build_oai_headers(kwargs)
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
        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    async def rerank(self, *args, **kwargs):
        """Rerank 接口（异步实现，移除了 v1 中的同步 httpx.Client）。"""
        headers = self._build_oai_headers(kwargs)
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

        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @HRModel.remote_callable
    async def image_generations(self, *args, **kwargs):
        """OpenAI Images Generations 接口（/v1/images/generations）。"""
        headers = self._build_oai_headers(kwargs)
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
        resp = await self.http_client.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            raise self._make_exception(kwargs, payload, url, resp)
        return resp.json()

    @HRModel.remote_callable
    async def anthropic_messages(self, *args, **kwargs) -> Union[Dict, AsyncGenerator]:
        """Anthropic Messages API（/v1/messages）。

        支持的客户端：Claude Code、OpenCode、cline、anthropic-sdk 等。各客户端
        在协议细节上的差异由 _normalize_anthropic_request 统一抹平，本函数只负责
        校验必填字段、解析 thinking、组装 payload、发请求。

        非流式返回 dict；流式返回 AsyncGenerator[bytes]（原始 SSE 字节）。
        """
        # 1. 必填校验
        for required in ("model", "messages", "max_tokens"):
            if required not in kwargs:
                raise ValueError(f"{required} parameter is required")

        # 2. headers（会从 kwargs 中 pop 掉 api_key / anthropic_version / anthropic_beta / extra_headers）
        headers = self._build_anthropic_headers(kwargs)

        # 3. 跨客户端兼容规整（messages / tools / tool_choice / 字段过滤）
        self._normalize_anthropic_request(kwargs)

        # 4. 提取主字段
        kwargs.pop("model")
        messages = kwargs.pop("messages")
        max_tokens = kwargs.pop("max_tokens")
        stream = kwargs.pop("stream", False)
        timeout = kwargs.pop("timeout", None) or 600.0

        # 5. thinking / reasoning（可能上浮 max_tokens）
        thinking, max_tokens = self._resolve_thinking(kwargs, max_tokens)

        # 6. 组装 payload，剩余 kwargs 视为 anthropic 合法字段透传
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

        # 7. 发请求
        url = self._build_anthropic_url("/v1/messages")
        if stream:
            return self._stream_bytes(self.anthropic_http_client, url, headers, payload, timeout)
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
        """Anthropic Count Tokens 接口（/v1/messages/count_tokens）。

        与 anthropic_messages 共享 _normalize_anthropic_request 规整逻辑。
        """
        # 1. 必填校验
        for required in ("model", "messages"):
            if required not in kwargs:
                raise ValueError(f"{required} parameter is required")

        # 2. headers
        headers = self._build_anthropic_headers(kwargs)

        # 3. 提取本函数特有字段
        extra_body: dict = kwargs.pop("extra_body", {}) or {}
        kwargs.pop("extra_query", None)
        timeout = kwargs.pop("timeout", None) or 120.0

        # 4. 跨客户端兼容规整
        self._normalize_anthropic_request(kwargs)

        # 5. 组装 payload
        kwargs.pop("model")
        messages = kwargs.pop("messages")
        payload: dict = {
            "model": self.engine,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if v is not None},
            **extra_body,
        }

        # 6. 发请求
        url = self._build_anthropic_url("/v1/messages/count_tokens")
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
    def bootstrap(worker_config, json_fields: set = None):
        """Worker 启动引导：三层配置合并 + 密钥管理 + 模型加载 + App 创建。

        优先级：代码默认值（dataclass）< JSON 运营覆盖 < CLI 显式传入。
        - JSON 只存放通过管理 API 显式修改的字段，不在启动时全量写入。
          这样修改 WorkerConfig 默认值后立即生效，不会被旧 JSON 覆盖。
        - CLI 显式传入的判定：运行时值与 dataclass 字段默认值不同。
        返回 (app, admin_key)。
        """
        if json_fields is None:
            json_fields = LLMRemoteModelV2._JSON_FIELDS
        import dataclasses
        import secrets as _secrets
        import string as _string
        from hepai.components.haiddf.worker.config_manager import WorkerConfigManager
        from hepai import HWorkerAPP
        from hepai.components.haiddf.worker.singletons import authorizer

        # 从 dataclass 反射拿到各字段的代码默认值
        code_defaults = {
            f.name: f.default
            for f in dataclasses.fields(worker_config)
            if f.name in json_fields and f.default is not dataclasses.MISSING
        }
        # 保存 parse_args 之后的运行时值（含 CLI 传入和默认值）
        cli_values = {k: getattr(worker_config, k) for k in json_fields}

        cfg_mgr = WorkerConfigManager(worker_id=worker_config.worker_name)

        # 三层合并：代码默认值 → JSON 运营覆盖 → CLI 显式传入
        merged = dict(code_defaults)
        json_worker = cfg_mgr.get_worker_config()
        if json_worker:
            merged.update({k: v for k, v in json_worker.items() if k in json_fields})
        for k, cli_v in cli_values.items():
            if cli_v != code_defaults.get(k):  # 与默认值不同 → CLI 显式传入
                merged[k] = cli_v
        for k, v in merged.items():
            setattr(worker_config, k, v)
        # 不在首次启动时全量写入 JSON，JSON 只存管理 API 的显式修改

        # secret key：只走 JSON，首次生成后持久化
        existing_key = cfg_mgr.get_secret_key()
        if existing_key:
            worker_config.secret_key = existing_key

        # 把 JSON metadata 中的 version 等运行时信息透传给 worker_config，
        # 以便 worker 注册到 controller 时 WorkerInfo.version 反映配置文件版本。
        json_metadata = cfg_mgr.get_metadata()
        json_version = json_metadata.get("version")
        if json_version:
            worker_config.version = json_version
        # 把整段 metadata 合并进 worker_config._metadata，供注册时上报
        existing_meta = getattr(worker_config, "_metadata", None) or {}
        merged_meta = {**existing_meta,
                       **{k: v for k, v in json_metadata.items()
                          if k not in ("secret_key", "admin_key")}}
        worker_config._metadata = merged_meta

        models = LLMRemoteModelV2.from_config(str(cfg_mgr.config_path))

        app = HWorkerAPP(models, worker_config=worker_config)

        if not existing_key and app.worker_secret_key:
            cfg_mgr.set_secret_key(app.worker_secret_key)

        # admin key：只走 JSON，首次生成后持久化
        admin_key = cfg_mgr.get_admin_key()
        if not admin_key:
            admin_key = ''.join(_secrets.choice(_string.ascii_letters + _string.digits)
                                for _ in range(12))
            cfg_mgr.set_admin_key(admin_key)
        authorizer.admin_key = admin_key

        app.state.cfg_mgr = cfg_mgr

        # 从 JSON 同步模型 enabled 初始状态
        for model in app.worker.models:
            model_data = cfg_mgr.get_model(model.name)
            if model_data and "enabled" in model_data:
                app.worker.set_model_enabled(model.name, model_data["enabled"])

        wk_info = app.worker.get_worker_info()
        print(wk_info, flush=True)
        print(f"🚀 Worker is running. {len(wk_info.resource_info)} available models:", flush=True)
        print(f"🔑 Admin key: `{admin_key}`", flush=True)
        return app

    @staticmethod
    def from_config(config_path: str) -> List["LLMRemoteModelV2"]:
        """从 worker_config.json 文件批量实例化模型对象。

        支持格式：
        {
          "metadata": { "version": "2.2", ... },
          "model": {
            "providers": {
              "<provider>": {
                "baseUrl": "...",
                "apiKey": "...",
                "models": [ {"id": "...", "engine": "...", ...}, ... ]
              }
            }
          }
        }
        旧字段名 meta / models 仍兼容读取。
        """
        with open(config_path, "r", encoding="utf-8") as f:
            cfg: Dict = json.load(f)

        metadata = cfg.get("metadata") or cfg.get("meta") or {}
        version = metadata.get("version", "2.0")

        providers = (cfg.get("model") or cfg.get("models") or {}).get("providers", {})
        models: List["LLMRemoteModelV2"] = []
        for provider_name, provider in providers.items():
            base_url = provider.get("baseUrl", "")
            api_key = provider.get("apiKey", "")
            need_external = provider.get("needExternalApiKey", False)
            provider_proxy = provider.get("proxy", None)
            provider_api_raw = provider.get("api", "openai-completions")
            provider_api_mode = provider_api_raw[0] if isinstance(provider_api_raw, list) else provider_api_raw
            anthropic_url = provider.get("anthropicUrl", None)

            for m in provider.get("models", []):
                model_id = m.get("id") or m.get("name")
                engine = m.get("engine") or model_id
                name = m.get("name") or model_id
                proxy = m.get("proxy", provider_proxy)
                api_raw = m.get("api", provider_api_mode)
                api_mode = api_raw[0] if isinstance(api_raw, list) else api_raw
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
                    anthropic_url=anthropic_url,
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
    anthropic_url: Optional[str] = field(default=None, metadata={"help": "Override base URL for anthropic-messages API. If None, use base_url directly."})
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
