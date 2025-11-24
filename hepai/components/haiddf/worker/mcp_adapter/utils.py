

from typing import List, Dict, Union
from ...base_class._worker_class import HRemoteModel
from starlette.applications import Starlette
from starlette.routing import Mount
# import contextlib
from contextlib import AsyncExitStack


# @contextlib.asynccontextmanager
# async def lifespan(app: Starlette):
#     async with contextlib.AsyncExitStack() as stack:
#         # await stack.enter_async_context(echo_mcp.session_manager.run())
#         await stack.enter_async_context(mcp.session_manager.run())
#         yield
        
        
def build_lifespan_for_starlette(models: List[HRemoteModel]):
    """
    创建适用于 Starlette 的 lifespan 函数
    """
    # 筛选出启用了 MCP 的模型
    models_with_mcp = [model for model in models if model.config.enable_mcp]
    
    async def _lifespan(app: Starlette):
        async with AsyncExitStack() as stack:
            # 为所有启用了 MCP 的模型启动会话
            for model in models_with_mcp:
                await stack.enter_async_context(model.mcp.session_manager.run())
            yield
    
    return _lifespan if models_with_mcp else None

def build_mcp_kwargs_for_starlette(
    models: HRemoteModel | List[HRemoteModel],
    route_prefix: str = "/apiv2"
    ):
    """
    To adapte to mcp server, the additional kwargs are needed.
    referes to: https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file
    """
    
    if not isinstance(models, list):
        models = [models]
        
    # 筛选出启用了 MCP 的模型
    models_with_mcp = [model for model in models if model.config.enable_mcp]
    if not models_with_mcp:  # no models with MCP enabled
        return {}
    
    mcp_transports = set(model.config.mcp_transport for model in models_with_mcp)
    if len(mcp_transports) > 1:
        raise ValueError(f"All models must have the same mcp_transport, but got: {mcp_transports}")
    mcp_transport = mcp_transports.pop()
    
    routes = []
    # lifespan = None
        
    for model in models:
        if not model.config.enable_mcp:
            continue
        # routes.append(Mount("/math", model.mcp.streamable_http_app()))
        # route_path = f'{route_prefix}/{model.name}'
        route_path = f"{route_prefix}/mcp/{model.model_id}"  # full path: /apiv2/mcp/{model_id}
        
        if mcp_transport == "streamable-http":
            routes.append(Mount(route_path, model.mcp.streamable_http_app()))
        elif mcp_transport == "sse":
            routes.append(Mount(route_path, model.mcp.sse_app()))
        else:
            raise ValueError(f"Unsupported mcp_transport: {mcp_transport}, only 'sse' and 'streamable-http' are supported.")
    
    
    
    if mcp_transport == "streamable-http":
        # 创建 lifespan 函数
        lifespan_func = build_lifespan_for_starlette(models_with_mcp)
        return {
            "routes": routes,
            "lifespan": lifespan_func
        }
    else:  # sse does not need lifespan
        return {
            "routes": routes,
            # "lifespan": lifespan
        }
            