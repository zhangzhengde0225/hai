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

    request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID", "system")
    token = request_id_context.set(request_id)
    try:
        logger.error(f"Unhandled Exception occurred at {request.method} {request.url.path}", exc_info=exc)
    finally:
        request_id_context.reset(token)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "The server encountered an error while processing the request."
        }
    )