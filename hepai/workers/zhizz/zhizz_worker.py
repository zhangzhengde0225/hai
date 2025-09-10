import os, sys
from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any
from dataclasses import dataclass, field
import uvicorn
import asyncio
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

import hepai as hai
from hepai import HRModel, HWorkerAPP, HModelConfig, HWorkerConfig
# from llm_remote_model import LLMRemoteModel, LLMModelConfig
from hepai.components.haiddf.base_class._llm_remote_model import LLMRemoteModel, LLMModelConfig



from dotenv import load_dotenv
load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量

   
def test_model():
    api_key = os.getenv("ZHIZENGZENG_API_KEY")
    
    model = "gpt-4.1"
    zhizz_model = LLMRemoteModel(config=ZhizzModelConfig(engine=model))
    stream = False  # Set to True if you want to test streaming
    stream = True
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": "say hello"}],
        "stream": stream,
        "api_key": api_key,
        "stream_options": {"include_usage": True},
    }
    rst_coro = zhizz_model.chat_completions(**kwargs)
    if stream:
        rst = asyncio.run(rst_coro)
        for chunk in rst:
            print(chunk)
    else:
        rst = asyncio.run(rst_coro)
        print(rst)


@dataclass
class ZhizzModelConfig(LLMModelConfig):
    config_file: Optional[str] = field(default=None, metadata={"help": "Path to the model configuration file, if None, load all models from the API"})
    ...

@dataclass
class ZhizzWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42602, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    # controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: payg, haichat, haiacademic, haioverleaf', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a zhizz worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(default=1000, metadata={"help": "Limit the model's concurrency"})
    
    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker, ensure the security, if enabled, the `api_key` must be provided when someone wants to access the worker's APIs"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})
    
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    
    debug: bool = field(default=True, metadata={"help": "Debug mode"})
    

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hai.parse_args((ZhizzModelConfig, ZhizzWorkerConfig))
    
    if model_config.test:
        test_model()
        # exit(0)
    
    from utils import load_models

    models: List[LLMRemoteModel] = load_models(model_config)  # Load models from the configuration file.
    app: FastAPI = HWorkerAPP(models, worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.

    wk_info = app.worker.get_worker_info()
    print(wk_info, flush=True)
    # 打印一下模型：
    print(f"🚀 Worker is running. {len(wk_info.resource_info)} available models:")
    # m_names = [m.model_name for m in wk_info.resource_info]
    # print_mns = m_names if len(m_names) <= 10 else m_names[:5] + ["..."] + m_names[-5:]
    # for m in print_mns:
    #     print(f"    - Model: {m}")
        # print(f" - Model: {m['name']}, Engine: {m.get('engine', 'N/A')}, Version: {m.get('version', 'N/A')}, Permission: {m.get('permission', 'N/A')}", flush=True)
    # 启动服务
    uvicorn.run(app, host=app.host, port=app.port)
    