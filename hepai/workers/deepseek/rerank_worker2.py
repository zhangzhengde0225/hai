import os, sys
from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any
from dataclasses import dataclass, field, asdict
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
    
    data = {
        "model": "bge-reranker-v2-m3",
        "query": "What is the capital of France?",
        "top_n": 2,
        "documents": [
            "The capital of Brazil is Brasilia.",
            "The capital of France is Paris.",
            "Horses and cows are both animals"
        ],
        "return_documents": False
    }
    
    stream = False  # Set to True if you want to test streaming
    # stream = True
    if stream:
        rst_gen = await llm.rerank(**data, stream=stream)
        async for chunk in rst_gen:
            print(chunk)
    else:
        rst = await llm.rerank(**data, stream=stream)
        print(rst)
        
def load_models_from_config(model_config: LLMModelConfig) -> List[LLMRemoteModel]:
    import yaml
    file_path = model_config.config_file
    assert file_path is not None and os.path.exists(file_path), f"Model configuration file not found: {file_path}"
    with open(file_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
        
    model_list = config_dict.get("models_list", [])
    assert len(model_list) > 0, "No models found in the configuration file"
    # 假设yaml顶层是一个列表，每个元素是一个模型配置
    models = []
    for m_cfg in model_list:
        # 只取LLMModelConfig支持的字段
        # 字段映射：model_name -> name
        if "model_name" in m_cfg:
            m_cfg["name"] = m_cfg.pop("model_name")
        allowed_keys = LLMModelConfig.__dataclass_fields__.keys()
        filtered_cfg = {k: v for k, v in m_cfg.items() if k in allowed_keys}
        exist_cfg_dict = asdict(model_config)
        exist_cfg_dict.update(filtered_cfg)  # 使用yaml中的字段覆盖默认配置
        cfg = LLMModelConfig(**exist_cfg_dict)
        models.append(LLMRemoteModel(config=cfg))
    return models


@dataclass
class ZhizzModelConfig(LLMModelConfig):
    config_file: str = field(default=None, metadata={"help": "Model's config file path"})
    name: str = field(default="hepai/bge-reranker-v2-m3", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    engine: str = field(default="bge-reranker-v2-m3", metadata={"help": "Model engine"})
    base_url: str = field(default="http://aigpu001.ihep.ac.cn:8001/v1", metadata={"help": "Base url of the zhizengzeng API"})
    _api_key: str = field(default=None, metadata={"help": "API key of the model"})
    test: bool = field(default=True, metadata={"help": "Test model"})

    def __post_init__(self):
        return super().__post_init__()

@dataclass
class ZhizzWorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=0, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    # controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: payg', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a zhizz worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    daemon: bool = field(default=False, metadata={"help": "Run as daemon"})
    limit_model_concurrency: int = field(default=1000, metadata={"help": "Limit the model's concurrency"})
    
    enable_secret_key: bool = field(default=False, metadata={"help": "Enable secret key for worker, ensure the security, if enabled, the `api_key` must be provided when someone wants to access the worker's APIs"})
    enable_llm_router: bool = field(default=True, metadata={"help": "Enable LLM router, only for llm worker"})


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hai.parse_args((ZhizzModelConfig, ZhizzWorkerConfig))
    
    # models: List[LLMRemoteModel] = load_models_from_config(model_config)
    models = [LLMRemoteModel(config=model_config)]
    
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
