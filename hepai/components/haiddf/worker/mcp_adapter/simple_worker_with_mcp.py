"""
HepAI - Custom Remote Model
"""
import json
try:
    from hepai import __version__
except:
    import os, sys
    from pathlib import Path
    here = Path(__file__).parent
    sys.path.insert(1, str(here.parent.parent))
    from hepai import __version__

from hepai import HRModel, HWorkerAPP, HWorkerConfig  # Import the HRModel class from the hepai package.

from mcp.server.fastmcp import FastMCP

# mcp = FastMCP(name="MathServer", stateless_http=True)

class SimpleWorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(self, name: str = "hepai/simple-model", **kwargs):
        super().__init__(name=name, **kwargs)

    # @HRModel.mcp.tool()
    @HRModel.remote_callable   # Decorate the function to enable remote call.
    async def simple_method(self, a: int = 1, b: int = 2) -> int:
        """Define your custom method here."""
        return a + b
    
    
import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount
# Create a combined lifespan to manage both session managers

model = SimpleWorkerModel(name="hepai/custom-model")  # Instantiate the custom worker model.
mcp = model.mcp

@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        # await stack.enter_async_context(echo_mcp.session_manager.run())
        await stack.enter_async_context(mcp.session_manager.run())
        yield

if __name__ == "__main__":
    # SimpleWorkerModel.run(
    #     routes=[
    #         Mount("/", math_mcp.streamable_http_app()),
    #     ]
    #     )  # Run the custom worker model.


    import uvicorn
    app = HWorkerAPP(
        model, worker_config=HWorkerConfig(),
        routes=[
            Mount("/math", mcp.streamable_http_app()),
        ], 
        lifespan=lifespan
        )  # Instantiate the APP, which is a FastAPI application.
    print(app.worker.get_worker_info(), flush=True)
    # 启动服务
    uvicorn.run(app, host=app.host, port=app.port)