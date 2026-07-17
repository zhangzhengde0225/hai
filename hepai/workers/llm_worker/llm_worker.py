import os
import sys
from typing import Optional, List, Literal, Union
from dataclasses import dataclass, field, fields as dc_fields
from pathlib import Path
here = Path(__file__).parent

# sys.path.insert(0, str(here.parent.parent.parent))

import hepai as hai
from hepai import HWorkerConfig, HWorkerAPP
from hepai import LLMRemoteModelV2 as LLMRemoteModel

from dotenv import load_dotenv

if os.path.exists(f"{here}/.env"):
    load_dotenv(f"{here}/.env")  # 优先加载当前目录的 .env 文件，方便不同 worker 定义不同的环境变量
elif os.path.exists(f"{here.parent.parent.parent}/.env"):
    load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量
else:
    load_dotenv()  # 默认加载当前工作目录及其父目录的 .env 文件


@dataclass
class WorkerConfig(HWorkerConfig):
    # 必填：决定 controller 注册标识 和 ~/.hepai/worker_configs/{worker_name}.json 配置文件路径
    # 用空字符串当 sentinel，在 __post_init__ 里校验（dataclass 继承不允许无默认值字段）
    worker_name: str = field(default="", metadata={"help": "[Required] Worker ID，用于定位 ~/.hepai/worker_configs/{worker_name}.json"})
    worker_id: str = field(default="", metadata={"help": "固定 worker_id，留空则自动生成并持久化到 JSON"})
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: Union[int, str, None] = field(default="auto", metadata={"help": "Worker's port"})

    controller_address: str = field(default="http://localhost:42501", metadata={"help": "Controller's address"})
    # controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})

    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})

    description: str = field(default="This is a zhizz worker of HEP AI framework (HepAI)", metadata={"help": "Model's description"})
    limit_model_concurrency: int = field(default=4096, metadata={"help": "Limit the model's concurrency"})
    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})
    type: Literal["llm", "actuator", "preceptor", "memory", "common"] = field(default="llm", metadata={"help": "Specify worker type, could be help in some cases"})

    def __post_init__(self):
        super().__post_init__()
        if not self.worker_name or not self.worker_name.strip():
            raise SystemExit(
                "[llm_worker] Error: --worker_name is required.\n"
                "  It identifies the worker on the controller and locates the persisted config at\n"
                "  ~/.hepai/worker_configs/{worker_name}.json\n"
                "  Example:  python llm_worker.py --worker_name=openrouter_cn ..."
            )
   

def _build_config_from_env() -> "WorkerConfig":
    """从环境变量构造 WorkerConfig，供 gunicorn / 其他 ASGI 服务器作为入口使用。

    支持的环境变量（与 WorkerConfig 字段同名，全大写）：
      WORKER_NAME（必填）、WORKER_ID、HOST、PORT、CONTROLLER_ADDRESS、NO_REGISTER、
      DESCRIPTION、LIMIT_MODEL_CONCURRENCY、ENABLE_SECRET_KEY、
      ENABLE_LLM_ROUTER、TYPE
    """
    kwargs = {}
    for f in dc_fields(WorkerConfig):
        env_key = f.name.upper()
        if env_key not in os.environ:
            continue
        raw = os.environ[env_key]
        # 简单类型转换
        if f.type is bool or f.default in (True, False):
            kwargs[f.name] = raw.strip().lower() in ("1", "true", "yes", "on")
        elif f.name == "port":
            kwargs[f.name] = int(raw) if raw.isdigit() else raw
        elif f.type is int or isinstance(f.default, int):
            kwargs[f.name] = int(raw)
        else:
            kwargs[f.name] = raw
    return WorkerConfig(**kwargs)


def create_app() -> HWorkerAPP:
    """ASGI app 工厂：供 `gunicorn -k uvicorn.workers.UvicornWorker llm_worker:create_app()` 使用。"""
    return LLMRemoteModel.bootstrap(_build_config_from_env())


# 当通过 gunicorn 等 ASGI 服务器以模块方式导入时，按需在模块级暴露 `app`
# （要求设置环境变量 WORKER_NAME）。
if os.environ.get("WORKER_NAME"):
    app: HWorkerAPP = create_app()


if __name__ == "__main__":
    import uvicorn
    worker_config: WorkerConfig = hai.parse_args(WorkerConfig)
    app = LLMRemoteModel.bootstrap(worker_config)
    uvicorn.run(app, host=app.host, port=app.port, loop="uvloop")
