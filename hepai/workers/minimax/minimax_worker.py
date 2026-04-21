import secrets
import string
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

here = Path(__file__).parent

sys.path.insert(0, str(here.parent.parent.parent))

import hepai as hai
from hepai import HWorkerAPP, HWorkerConfig
from hepai.components.haiddf.base_class._llm_remote_model_v2 import (
    LLMRemoteModelV2 as LLMRemoteModel,
)
from hepai.components.haiddf.worker.singletons import authorizer
from hepai.workers.minimax.config_manager import WorkerConfigManager

from dotenv import load_dotenv

load_dotenv(f"{here.parent.parent.parent}/.env")


@dataclass
class WorkerConfig(HWorkerConfig):
    worker_name: str = field(
        default="minimax",
        metadata={
            "help": "Worker ID，用于定位 ~/.hepai/worker_configs/{worker_id}_worker.json"
        },
    )
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address"})
    port: int = field(default=42606, metadata={"help": "Worker's port"})
    auto_start_port: int = field(
        default=42606,
        metadata={"help": "Worker's start port, only used when port is set to `auto`"},
    )
    controller_address: str = field(
        default="http://aiapi.ihep.ac.cn:42601",
        metadata={"help": "Controller's address"},
    )
    route_prefix: str = field(
        default="/apiv2", metadata={"help": "Route prefix for worker"}
    )
    no_register: bool = field(
        default=False, metadata={"help": "Do not register to controller"}
    )
    permissions: str = field(default=None, metadata={"help": "Model permissions"})
    description: str = field(
        default="Local Minimax OpenAI-compatible worker",
        metadata={"help": "Model description"},
    )
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(
        default=1000, metadata={"help": "Limit the model's concurrency"}
    )
    enable_secret_key: bool = field(
        default=True, metadata={"help": "Enable secret key for worker"}
    )
    enable_llm_router: bool = field(
        default=True, metadata={"help": "Enable LLM router, only for llm worker"}
    )
    model_config_dir: Optional[str] = field(
        default=str(here), metadata={"help": "Directory to store worker_config.json"}
    )
    is_free: bool = field(
        default=False, metadata={"help": "Whether the model is free to use"}
    )
    debug: bool = field(default=True, metadata={"help": "Debug mode"})
    secret_key: Optional[str] = field(
        default=None,
        metadata={
            "help": "Worker secret key; if None, will be generated and persisted to config"
        },
    )


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    worker_config: WorkerConfig = hai.parse_args(WorkerConfig)
    cfg_mgr = WorkerConfigManager(worker_id=worker_config.worker_name)

    worker_fields = [
        "host",
        "port",
        "auto_start_port",
        "controller_address",
        "route_prefix",
        "no_register",
        "permissions",
        "description",
        "daemon",
        "limit_model_concurrency",
        "enable_secret_key",
        "enable_llm_router",
        "is_free",
        "debug",
    ]

    json_worker = cfg_mgr.get_worker_config()
    if json_worker:
        for k, v in json_worker.items():
            if hasattr(worker_config, k):
                setattr(worker_config, k, v)
    else:
        cfg_mgr.set_worker_config({f: getattr(worker_config, f) for f in worker_fields})

    existing_key = cfg_mgr.get_secret_key()
    if existing_key:
        worker_config.secret_key = existing_key

    models: List[LLMRemoteModel] = LLMRemoteModel.from_config(str(cfg_mgr.config_path))
    app: FastAPI = HWorkerAPP(models, worker_config=worker_config)

    if not existing_key and app.worker_secret_key:
        cfg_mgr.set_secret_key(app.worker_secret_key)

    admin_key = cfg_mgr.get_admin_key()
    if not admin_key:
        chars = string.ascii_letters + string.digits
        admin_key = "".join(secrets.choice(chars) for _ in range(8))
        cfg_mgr.set_admin_key(admin_key)
    authorizer.admin_key = admin_key

    app.state.cfg_mgr = cfg_mgr

    for model in app.worker.models:
        model_data = cfg_mgr.get_model(model.name)
        if model_data and "enabled" in model_data:
            app.worker.set_model_enabled(model.name, model_data["enabled"])

    wk_info = app.worker.get_worker_info()
    print(wk_info, flush=True)
    print(
        f"🚀 Minimax worker is running. {len(wk_info.resource_info)} available models:"
    )
    print(f"🔑 Admin key: `{admin_key}`", flush=True)
    uvicorn.run(app, host=app.host, port=app.port)
