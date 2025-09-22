"""
自定义模型，由HaiDDF搭载，实现远程服务和调用
"""
from dataclasses import dataclass, field
import uvicorn

import hepai as hai
# from hepai._types import HWorkerModel, HWorkerArgs, HWorkerAPP

try:
    from haiddf.version import __version__
except:
    from pathlib import Path
    here = Path(__file__).parent
    import os, sys
    sys.path.insert(1, str(here.parent.parent.parent))
    from haiddf.version import __version__
from haiddf._types import HWorkerModel, HWorkerArgs
# from hepai._types import HWorkerModel, HWorkerArgs
from worker_app import HWorkerAPP

# 继承HWorkerModel类，实现自定义类
class CustomWorkerModel(HWorkerModel):
    def __init__(self, name: str = "hepai/custom-model"):
        super().__init__(name=name)

    @HWorkerModel.remote_callable  # 用该修饰器标记为可远程调用的方法
    def custom_method(self, a: int, b: int) -> int:
        """你可以在这里定义你的自定义方法和返回值"""
        return a + b

@dataclass
class CustomWorkerArgs(HWorkerArgs):
    """
    自定义参数类，继承自HWorkerArgs，
        - 可在此处定义自己的默认参数，添加新的参数
        - 也可以在程序运行时通过命令行传入参数，例如：--no_register True
    """
    pass
    
if __name__ == "__main__":
    # 实例化模型
    model = CustomWorkerModel(name="hepai/custom-model")
    # 解析命令行参数
    worker_config = hai.parse_args(CustomWorkerArgs)
    # 实例化APP，是一个fastapi应用
    app = HWorkerAPP(model, worker_config=worker_config)
    print(app.worker.get_worker_info(), flush=True)
    # 启动服务
    uvicorn.run(app, host=app.host, port=app.port)



