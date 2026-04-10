import os, sys
from typing import List, Optional
from dataclasses import dataclass, field
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

import hepai as hai
from hepai import HWorkerAPP, HWorkerConfig
from hepai.components.haiddf.base_class._llm_remote_model_v2 import (
    LLMRemoteModelV2 as LLMRemoteModel,
)
from hepai.tools.llm_connectivity_evaluator import LLMConenctivityEvaluator
from hepai.workers.openrouter.config_manager import WorkerConfigManager

from dotenv import load_dotenv
load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量


@dataclass
class WorkerConfig(HWorkerConfig):
    worker_name: str = field(default="openrouter", metadata={"help": "Worker ID，用于定位 ~/.hepai/worker_configs/{worker_id}.json"})

    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42605, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    controller_address: str = field(default="http://localhost:42500", metadata={"help": "Controller's address"})

    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    no_register: bool = field(default=True, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: payg; owner: admin', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a zhizz worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(default=1000, metadata={"help": "Limit the model's concurrency"})

    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker, ensure the security, if enabled, the `api_key` must be provided when someone wants to access the worker's APIs"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})
    model_config_dir: Optional[str] = field(default=str(here), metadata={"help": "Directory to store model_config.yaml, if None, will try to use worker script directory or current working directory"})
    is_free: bool = field(default=False, metadata={"help": "Whether the model is free to use, if False, model owner should setup model pricing via controller"})
    debug: bool = field(default=True, metadata={"help": "Debug mode"})

    

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    worker_config: WorkerConfig = hai.parse_args(WorkerConfig)

    # 持久化配置管理器：自动定位 ~/.hepai/worker_configs/{worker_id}.json
    cfg_mgr = WorkerConfigManager(worker_id=worker_config.worker_name)

    models: List[LLMRemoteModel] = LLMRemoteModel.from_config(str(cfg_mgr.config_path))

    LLMConenctivityEvaluator().run(models)

    app: FastAPI = HWorkerAPP(models, worker_config=worker_config)

    # 将 cfg_mgr 挂载到 app，方便在其他模块中访问
    app.state.cfg_mgr = cfg_mgr

    wk_info = app.worker.get_worker_info()
    print(wk_info, flush=True)
    print(f"🚀 Worker is running. {len(wk_info.resource_info)} available models:")
    uvicorn.run(app, host=app.host, port=app.port)
    