import sys
from typing import Optional, List, Literal
from dataclasses import dataclass, field
from pathlib import Path
here = Path(__file__).parent

sys.path.insert(0, str(here.parent.parent.parent))

import hepai as hai
from hepai import HWorkerConfig, HWorkerAPP
from hepai import LLMRemoteModelV2 as LLMRemoteModel

from dotenv import load_dotenv
load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量


@dataclass
class WorkerConfig(HWorkerConfig):
    worker_name: str = field(default="openrouter", metadata={"help": "Worker ID，用于定位 ~/.hepai/worker_configs/{worker_id}.json"})
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42605, metadata={"help": "Worker's port"})
    
    # controller_address: str = field(default="http://localhost:42501", metadata={"help": "Controller's address"})
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    
    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    
    description: str = field(default="This is a zhizz worker of HEP AI framework (HepAI)", metadata={"help": "Model's description"})
    limit_model_concurrency: int = field(default=1000, metadata={"help": "Limit the model's concurrency"})
    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})
    type: Literal["llm", "actuator", "preceptor", "memory", "common"] = field(default="llm", metadata={"help": "Specify worker type, could be help in some cases"})
   

if __name__ == "__main__":
    import uvicorn
    worker_config: WorkerConfig = hai.parse_args(WorkerConfig)
    app: HWorkerAPP = LLMRemoteModel.bootstrap(worker_config)
    uvicorn.run(app, host=app.host, port=app.port)
    