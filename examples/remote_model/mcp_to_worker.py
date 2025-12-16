
"""
本案例提供了便捷的将MCP工具通过无限函数协议搭载到Worker节点上的代码。   
"""

from mcp.server.fastmcp import FastMCP
from dataclasses import dataclass, field
import hepai as hai
from hepai import HModelConfig, HWorkerConfig
from hepai import HaiMCP


mcp = HaiMCP(
    name="CTReconstruct",
    instructions="Some tools for showing and reconstructing CT images.",
    host="0.0.0.0",
    port = 42502, 
    )

# Add an addition tool
@mcp.tool()
async def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@dataclass
class CustomWorkerConfig(HWorkerConfig):
    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    permissions: str = field(default='users: admin; groups: payg; owner:zdzhang@ihep.ac.cn', metadata={"help": "Worker's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    type: str = field(default="mcp_tool", metadata={"help": "Specify worker type, could be help in some cases"})    

if __name__ == "__main__":
    
    worker_config = hai.parse_args((CustomWorkerConfig, ))[0]
    
    mcp.run_via_worker(
        transport="sse",
        worker_config=worker_config,
        model_config=None,  # 预留自主定义模型配置的接口，可传入HModelConfig()类实例
        )
    

