"""单进程启动 weidijia worker，用于 VSCode F5 调试。

等价于 run_weidijia_worker_gunicorn.sh，但不使用 gunicorn 多进程，
直接用 uvicorn 单进程跑，方便断点调试。
"""
import os
import uvicorn

os.environ.setdefault("WORKER_NAME", "weidijia")
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "42602")
# os.environ.setdefault("CONTROLLER_ADDRESS", "http://localhost:42501")
os.environ.setdefault("CONTROLLER_ADDRESS", "https://aiapi.ihep.ac.cn")
os.environ.setdefault("NO_REGISTER", "false")

from hepai.workers.llm_worker.llm_worker import create_app

if __name__ == "__main__":
    print(f"[debug] WORKER_NAME       = {os.environ['WORKER_NAME']}")
    print(f"[debug] bind              = {os.environ['HOST']}:{os.environ['PORT']}")
    print(f"[debug] CONTROLLER_ADDRESS= {os.environ['CONTROLLER_ADDRESS']}")

    app = create_app()
    uvicorn.run(
        app,
        host=os.environ["HOST"],
        port=int(os.environ["PORT"]),
        loop="uvloop",
    )
