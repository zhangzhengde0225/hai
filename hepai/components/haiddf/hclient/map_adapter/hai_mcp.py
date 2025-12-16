"""
HepAI对MCP的封装，实现将MCP工具方便地搭载到Worker节点上，同时支持MCP协议和HepAI无限函数协议。
"""

from typing import Literal
from mcp.server.fastmcp import FastMCP
# from hepai import HRModel, HModelConfig, HWorkerConfig, HWorkerAPP

from ...base_class._worker_class import HRModel, HModelConfig
from ...worker._worker_class import HWorkerConfig
from ...worker.worker_app import HWorkerAPP


class HaiMCP(FastMCP):
    """HepAI对MCP的封装，实现将MCP工具方便地搭载到Worker节点上，同时支持MCP协议和HepAI无限函数协议。"""

    def __init__(self, **kwargs):
        """初始化HaiMCP实例，继承自FastMCP。"""
        super().__init__(**kwargs)
        
        self.mcp_config_dict = kwargs  # 保存初始化参数以备后续使用
        
        
    def run(
        self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        mount_path: str | None = None,
    ) -> None:
        
        super().run(transport=transport, mount_path=mount_path)
        
        
    def run_via_worker(
        self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        mount_path: str | None = None,
        model_config: HModelConfig | None = None,
        worker_config: HWorkerConfig | None = None,
    ) -> None:
        """把MCP搭载到WorkerModel上"""
        
        model_cfg = model_config if model_config is not None else HModelConfig()
        model_cfg.enable_mcp = True
        model_cfg.mcp_transport = transport
        
        if "/" in str(self.name):
            name = self.name
        else:
            name = f'hepai/{self.name}'  # 自动添加前缀
            
        model = HRModel(
            name=name,
            config=model_cfg,
            mcp=self,  # 把自己传给model
        )
        
        config_dict = self.mcp_config_dict.copy()
        config_dict = {
            k: v for k, v in config_dict.items() if k in HWorkerConfig.__dataclass_fields__
        }
        # worker_cfg = HWorkerConfig.from_dict(config_dict)
        worker_cfg = worker_config if worker_config is not None else HWorkerConfig()
        worker_cfg.update_from_dict(config_dict)
        
        app = HWorkerAPP(
            models=[model],
            worker_config=worker_cfg,
        )
        print(app.worker.get_worker_info(), flush=True)
        
        import uvicorn
        uvicorn.run(app, host=app.host, port=app.port)
        
        