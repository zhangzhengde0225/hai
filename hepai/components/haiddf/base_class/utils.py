import functools
import json
from typing import Dict, Any


def add_request_context_to_exception(e: Exception, original_kwargs: Dict[str, Any]) -> None:
    """
    为异常对象追加请求上下文便签 (仅支持 Python 3.11+)。
    提取 模型、流模式、User-Agent 等片段，不会破坏原始堆栈。
    """
    try:
        extra_headers = original_kwargs.get("extra_headers", {})

        # 1. 提取关键上下文
        user_agent = extra_headers.get("user-agent") or extra_headers.get("User-Agent", "Unknown")
        user_info = extra_headers.get("x-user-id") or extra_headers.get("x-user-email", "Unknown")

        # 👉 新增提取 model 和 stream
        req_model = original_kwargs.get("model", "Unknown")
        req_stream = original_kwargs.get("stream", "未传参(通常默认False)")

        # 2. 安全处理 kwargs (防刷屏 + 彻底移除敏感信息)
        safe_kwargs = original_kwargs.copy()

        safe_kwargs.pop("api_key", None)

        if "messages" in safe_kwargs and isinstance(safe_kwargs["messages"], list):
            safe_kwargs["messages"] = f"<List of {len(safe_kwargs['messages'])} messages>"

        # 使用 default=str 防止遇到无法序列化的对象导致二次崩溃
        payload_str = json.dumps(safe_kwargs, ensure_ascii=False, default=str)
        if len(payload_str) > 500:
            payload_str = payload_str[:500] + "...[截断]"

        # 3. 构建便签内容 (增加 model 和 stream 展示)
        note_content = (
            f"\n[Worker 运行上下文诊断]:"
            f"\n  |- 请求模型: {req_model}"
            f"\n  |- Stream模式: {req_stream}"
            f"\n  |- User-Agent: {user_agent}"
            f"\n  |- 潜在用户: {user_info}"
            f"\n  |- 剩余参数键: {list(safe_kwargs.keys())}"
            f"\n  |- 载荷预览: {payload_str}"
        )

        # 追加便签
        e.add_note(note_content)

    except Exception as fallback_e:
        # 极端情况：如果提取上下文的过程报错，留下一个简化的便签
        e.add_note(f"\n[Worker 运行上下文诊断]: 提取上下文时发生异常: {repr(fallback_e)}")


def inject_context_on_error(func):
    """异常时自动拦截 kwargs 并追加到报错便签的装饰器"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            add_request_context_to_exception(e, kwargs)
            raise

    return wrapper