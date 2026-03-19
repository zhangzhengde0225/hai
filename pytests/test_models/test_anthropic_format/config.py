import os
from dataclasses import dataclass, field
from pathlib import Path

here = Path(__file__).parent
repo_root = here.parent.parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(repo_root / ".env")
except ImportError:
    pass


@dataclass
class PresetServerConfig:
    api_key: str = None
    base_url: str = None

@dataclass
class PresetZhizzServer(PresetServerConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("ZHIZENGZENG_API_KEY", ""))
    base_url: str = "https://api.zhizengzeng.com/anthropic/"

@dataclass
class PresetDDFServer(PresetServerConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("HEPAI_API_KEY", ""))
    base_url: str = "https://aiapi.ihep.ac.cn/apiv2/anthropic/"


@dataclass
class PresetLocalDDFServer(PresetServerConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("HEPAI_API_KEY", ""))
    base_url: str = "http://localhost:42500/apiv2/anthropic/"


@dataclass
class PresetWorkerServer(PresetServerConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("3090_WORKER_API_KEY", ""))
    base_url: str = "http://localhost:42605/apiv2/anthropic/"


@dataclass
class PresetMinimaxServer(PresetServerConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("MINIMAX_API_KEY", ""))
    base_url: str = "https://api.minimaxi.com/anthropic/"


@dataclass
class TestConfig:
    client: PresetServerConfig = field(default_factory=PresetLocalDDFServer)
    # client: PresetServerConfig = field(default_factory=PresetWorkerServer)
    # client: PresetServerConfig = field(default_factory=PresetZhizzServer)
    # client: PresetServerConfig = field(default_factory=PresetMinimaxServer)

    # model: str = "minimax/minimax-m2.5"
    model: str = "minimax/minimax-m2.7-highspeed"
    # model: str = "anthropic/claude-sonnet-4-6"
    # model: str = "MiniMax-M2.7"


    def __post_init__(self):
        if isinstance(self.client, PresetZhizzServer) or isinstance(self.client, PresetMinimaxServer):
            self.model = self.model.split("/")[-1]  # For Zhizz and Minimax servers, model name should not include the "anthropic/" prefix



# 默认配置实例，供各测试文件直接导入使用
default_config = TestConfig()
