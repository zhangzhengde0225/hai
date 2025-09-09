
from hepai.types import LLMRemoteModel, LLMModelConfig
from hepai import HepAI
import os
from pathlib import Path
from dataclasses import asdict
from dotenv import load_dotenv

here = Path(__file__).parent
load_dotenv(f'{here.parent.parent.parent}/.env')


def load_models(model_config: "LLMModelConfig"):
    """加载模型配置文件中的模型"""
    if model_config.config_file is None:
        # 动态获取所有可用模型
        api_key = model_config.api_key
        base_url = model_config.base_url
        
        client = HepAI(api_key=api_key, base_url=base_url)
        try:
            models_res = client.models.list()
            model_names = list(set([x.id.lower() for x in models_res]))

            models = []

            for model in model_names:
                engine = model
                provider = get_provider_by_model_name(model)
                if provider is None:
                    print(f"Skipping unknown provider model: {model}")
                    continue
                model_name = f"{provider}/{engine}"  # 设置为provider/engine格式
                
                cfg = LLMModelConfig(
                    name=model_name,
                    engine=engine,
                    base_url=model_config.base_url,
                    _api_key=model_config._api_key,
                    proxy=model_config.proxy,
                    need_external_api_key=model_config.need_external_api_key,
                    permission=model_config.permission,
                    version=model_config.version,
                    enable_async=model_config.enable_async,
                    test=model_config.test
                )
                models.append(LLMRemoteModel(config=cfg))
            
            print(f"Successfully loaded {len(models)} models from {base_url}.")
            return models
            
        except Exception as e:
            print(f"Failed to load models from API: {e}")
            # 如果API调用失败，回退到原来的单模型模式
            models = [LLMRemoteModel(config=model_config)]
    else:
        import yaml
        with open(model_config.config_file, "r", encoding="utf-8") as f:
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

def get_provider_by_model_name(model_name: str) -> str:
    """
    根据模型名字获得provider。
    例如: chatgpt类模型->openai, deepseek类模型->deepseek-ai, qwen类模型->aliyun。
    未知模型抛出异常。
    """
    name = model_name.lower()
    
    if "deepseek" in name:
        return "deepseek-ai"
    elif "grok" in name:
        return "xAI"
    elif "ernie" in name or name == 'x1':
        return "baidu"
    elif "360zhinao" in name:
        return "360"
    elif "claude" in name:
        return "anthropic"
    elif "hunyuan" in name:
        return "tencent"
    elif "gemini" in name:
        return "google"
    elif "glm" in name:
        return "zhipu"
    elif "baichuan" in name:
        return "baichuan"
    elif "doubao" in name:
        return "bytedance"
    elif any(x in name for x in ["qwen", "qianwen", "aliyun", "qwq"]):
        return "aliyun"
    elif any(x in name for x in ["minimax", "abab"]):
        return "minimax"
    elif any(x in name for x in ["kimi", "moonshot"]):
        return "moonshot"
    elif "llama" in name:
        return "meta"
    elif "yi" in name:
        return "01-ai"
    # elif any(x in name for x in ["generalv3", "4.0ultra"]):
    elif name in ["generalv3", "4.0ultra", "pro-128k", "max-32k", "lite", 'generalv3.5']:
        return "iflytech"
    elif any(x in name for x in ["gpt", "chatgpt", "openai", "o1", "o3", "o4", "tts-1",
                                 "text-embedding", "dall-e", "whisper-1"]):
        return "openai"
    elif name in ['max-32k', "lite"]:
        return None
    else:
        raise ValueError(f"未知模型provider: {model_name}")