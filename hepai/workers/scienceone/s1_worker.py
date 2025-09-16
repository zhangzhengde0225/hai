import os, sys
from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any
from dataclasses import dataclass, field
import uvicorn
from pathlib import Path
import asyncio

here = Path(__file__).parent
try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

import hepai as hai
from hepai import HepAI
from hepai import HRModel, HWorkerAPP, HModelConfig, HWorkerConfig
from hepai.components.haiddf.base_class._llm_remote_model import LLMRemoteModel, LLMModelConfig


from dotenv import load_dotenv
load_dotenv(f"{here.parent.parent.parent}/.env")  # 加载环境变量

   
async def test_model(model_config, models: List[LLMRemoteModel]):
    cfg: LLMModelConfig = model_config
    # client = HepAI(api_key=cfg.api_key, base_url=cfg.base_url) # set proxy to base_url
    # models = client.models.list()
    # for model in models:
    #     print(f'  {model}')
    
    engine = models[0].engine
    
    llm = LLMRemoteModel(config=ZhizzModelConfig(engine=engine))
    
    
    stream = False  # Set to True if you want to test streaming
    stream = True
    kwargs = {
        "model": models[0].name,
        "messages": [{"role": "user", "content": "hello"}],
        "stream": stream,
        "api_key": cfg.api_key,
        "stream_options": {"include_usage": True},
    }
    if stream:
        rst_gen = await llm.chat_completions(**kwargs)
        async for chunk in rst_gen:
            print(chunk)
    else:
        rst = await llm.chat_completions(**kwargs)
        print(rst)


@dataclass
class ZhizzModelConfig(LLMModelConfig):
    config_file: Optional[str] = field(default=f"{here}/model_config.yaml", metadata={"help": "Path to the model configuration file, if None, load all models from the API"})
    base_url: str = field(default="https://uni-api.cstcloud.cn/v1", metadata={"help": "Base url of the zhizengzeng API"})
    _api_key: str = field(default="os.environ/SCIENCEONE_API_KEY", metadata={"help": "API key of the model"})
    test: bool = field(default=True, metadata={"help": "Test model"})

    def __post_init__(self):
        return super().__post_init__()

@dataclass
class ZhizzWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=42602, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: payg', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a zhizz worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    # author: str = field(default="", metadata={"help": "Model's author"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(default=1000, metadata={"help": "Limit the model's concurrency"})
    
    enable_secret_key: bool = field(default=True, metadata={"help": "Enable secret key for worker, ensure the security, if enabled, the `api_key` must be provided when someone wants to access the worker's APIs"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hai.parse_args((ZhizzModelConfig, ZhizzWorkerConfig))
    
    
    from hepai.workers.zhizz.utils import load_models
    models: List[LLMRemoteModel] = load_models(model_config)  # Load models from the configuration file.
    
    if model_config.test:
        asyncio.run(test_model(model_config, models))
  
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
