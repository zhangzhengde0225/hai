from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from hepai.tools.logger import Logger
from hepai.tools.request_context import request_id_context

logger = Logger.get_logger("global_error_handler")


async def global_unhandled_exception_handler(request: Request, exc: Exception):
    """全局兜底：拦截所有未捕获异常"""

    if isinstance(exc, (HTTPException, StarletteHTTPException, RequestValidationError)):
        raise exc

    # 防止重复记录
    if getattr(exc, "__logged__", False):
        # 如果已经发过头了（针对流式响应），直接结束，不再尝试返回 JSON
        if request.scope.get("type") == "http" and await request.is_disconnected():
            return
        # 否则只返回响应，不打日志
        return _build_500_response()

    request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID", "system")
    token = request_id_context.set(request_id)

    try:
        # 标记为已记录
        setattr(exc, "__logged__", True)

        log_exc = exc
        if isinstance(exc, ExceptionGroup) and len(exc.exceptions) == 1:
            log_exc = exc.exceptions[0]

        logger.error(f"Unhandled Exception at {request.method} {request.url.path}", exc_info=log_exc)
    finally:
        request_id_context.reset(token)

    return _build_500_response()


def _build_500_response():
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "The server encountered an error while processing the request."
        }
    )