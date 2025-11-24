"""
HepAI - Custom Remote Model
"""
import json
try:
    from hepai import __version__
except:
    import os, sys
    from pathlib import Path
    here = Path(__file__).parent
    sys.path.insert(1, str(here.parent.parent))
    from hepai import __version__

from hepai import HRModel  # Import the HRModel class from the hepai package.

class SimpleWorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(self, name: str = "hepai/simple-model", **kwargs):
        super().__init__(name=name, **kwargs)

    @HRModel.remote_callable  # Decorate the function to enable remote call.
    def simple_method(self, a: int = 1, b: int = 2) -> int:
        """Define your custom method here."""
        return a + b

if __name__ == "__main__":
    SimpleWorkerModel.run()  # Run the custom worker model.


    # import uvicorn
    # model = SimpleWorkerModel(name="hepai/custom-model")  # Instantiate the custom worker model.
    # app = HWorkerAPP(model, worker_config=HWorkerConfig())  # Instantiate the APP, which is a FastAPI application.
    # print(app.worker.get_worker_info(), flush=True)
    # # 启动服务
    # uvicorn.run(app, host=app.host, port=app.port)