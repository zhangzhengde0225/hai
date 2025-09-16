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
import hepai as hai
from hepai import HRModel, HModelConfig, HWorkerConfig, HWorkerAPP

@dataclass
class CustomModelConfig(HModelConfig):
    name: str = field(default="hepai/custom-model", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})

@dataclass
class CustomWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=4260, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})
    # controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    
    controller_prefix: str = field(default="/apiv2", metadata={"help": "Controller's route prefix"})
    
    speed: int = field(default=1, metadata={"help": "Model's speed"})
    limit_model_concurrency: int = field(default=5, metadata={"help": "Limit the model's concurrency"})
    stream_interval: float = field(default=0., metadata={"help": "Extra interval for stream response"})
    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin;groups: payg', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a demo worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    author: str = field(default=None, metadata={"help": "Model's author"})
    api_key: str = field(default="", metadata={"help": "API key for reigster to controller, ensure the security"})
    debug: bool = field(default=False, metadata={"help": "Debug mode"})
    type: Literal["llm", "actuator", "preceptor", "memory", "common"] = field(default="agent", metadata={"help": "Specify worker type, could be help in some cases"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})

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
            
            
    @HRModel.remote_callable
    def get_info(self) -> Dict[str, Union[str, int]]:
        """Get model info."""
        return {
            "name": self.name,
        }

if __name__ == "__main__":

    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hai.parse_args((CustomModelConfig, CustomWorkerConfig))
    model = CustomWorkerModel(model_config)  # Instantiate the custom worker model.
    app: FastAPI = HWorkerAPP(model, worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.
    
    print(app.worker.get_worker_info(), flush=True)
    # 启动服务
    uvicorn.run(app, host=app.host, port=app.port)