

"""
    ### anthropic: v0.59.0
支持claude code 2.0.5，但不支持2.0.62
报错：API Error: 400 {"detail":"RuntimeError: Async function raised an error, please check the function. AsyncMessages.create() got an unexpected keyword argument 'context_management'\nRuntimeError: Async function raised an error, please check the function. AsyncMessages.create() got an unexpected 
    keyword argument 'context_management'"}
原因是：0.59.0版本的anthropic包不支持context_management参数

"""
from typing import List, Optional


from hepai.workers.zhizz.zhizz_worker import ZhizzModelConfig, ZhizzWorkerConfig
from hepai.components.haiddf.base_class._llm_remote_model import LLMRemoteModel, LLMModelConfig
from hepai.workers.zhizz.utils import load_models

import uvicorn
from fastapi import FastAPI
import hepai as hai
    
model_config, worker_config = hai.parse_args((ZhizzModelConfig, ZhizzWorkerConfig))
models: List[LLMRemoteModel] = load_models(model_config)  # Load models from the configuration file.

model = [x for x in models if x.config.name == "claude-sonnet-4-5-20250929"][0]


async def main():
    
    
    
    gen = await model.anthropic_stream(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": "写一首关于春天的诗"}],
        max_tokens=1024,
        stream=True,
    )




