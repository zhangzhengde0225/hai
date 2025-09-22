"""
HepAI - Custom Remote Model
"""

try:
    from hepai import __version__
except:
    import os, sys
    from pathlib import Path
    here = Path(__file__).parent
    sys.path.insert(1, str(here.parent.parent))
    from hepai import __version__


from typing import Dict, Union, Literal
from dataclasses import dataclass, field
import json
import hepai
from hepai import HRModel, HModelConfig, HWorkerConfig, HWorkerAPP

@dataclass  # (1) model config
class CustomModelConfig(HModelConfig):
    name: str = field(default="hepai/custom-model", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    enable_mcp: bool = field(default=True, metadata={"help": "Enable MCP router"})

@dataclass  # (2) worker config
class CustomWorkerConfig(HWorkerConfig):
    # config for worker server
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42600, metadata={"help": "Worker's port, default is 42600"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `None`"})
    type: Literal["common", "llm", "actuator", "preceptor", "memory"] = field(default="common", metadata={"help": "Specify worker type, could be help in some cases"})
    speed: int = field(default=1, metadata={"help": "Model's speed"})
    limit_model_concurrency: int = field(default=100, metadata={"help": "Limit the model's concurrency"})
    permissions: str = field(default='users: admin;groups: payg', metadata={"help": "Worker's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    author: str = field(default=None, metadata={"help": "Model's author"})
    description: str = field(default='This is a custom remote worker created by HepAI.', metadata={"help": "Model's description"})
    
    # config for controller connection
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    no_register: bool = field(default=True, metadata={"help": "Do not register to controller"})

class CustomWorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(self, config: HModelConfig):
        super().__init__(config=config)

    @HRModel.remote_callable  # Decorate the function to enable remote call.
    def custom_method(self, a: int = 1, b: int = 2) -> int:
        """Define your custom method here."""
        return a + b
    
    @HRModel.remote_callable
    def get_stream(self):
        for x in range(10):
            yield f"data: {json.dumps(x)}\n\n"
            
if __name__ == "__main__":

    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hepai.parse_args((CustomModelConfig, CustomWorkerConfig))
    model = CustomWorkerModel(model_config)  # Instantiate the custom worker model.
    app: FastAPI = HWorkerAPP(models=[model], worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.
    
    print(app.worker.get_worker_info(), flush=True)
    # 启动服务  
    uvicorn.run(app, host=app.host, port=app.port)