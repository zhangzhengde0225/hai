# HepAI LLM Worker —— 一键启动镜像
#
# 构建（必须在仓库根目录执行；构建上下文 = 仓库根）：
#   docker build -f hepai/workers/llm_worker/Dockerfile -t hepai-llm-worker:latest .
#
# 运行：
#   docker run --rm -p 42505:42505 --env-file .env \
#       --add-host=host.docker.internal:host-gateway \
#       hepai-llm-worker:latest \
#       --controller_address=http://host.docker.internal:42501
#
# 也可以直接用同目录下的 build.sh / run.sh。

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    TZ=Asia/Shanghai

WORKDIR /app

# slim 已自带 ca-certificates；tzdata/curl 用不到，省一层 apt
# 先装 Python 依赖，利用层缓存
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# 复制源码：hepai/__init__.py 内部 `from hai import *`，所以 hai/ 也必须带上
COPY hai  /app/hai
COPY hepai /app/hepai

EXPOSE 42505-42605

ENTRYPOINT ["python", "/app/hepai/workers/llm_worker/llm_worker.py"]
# port=none 表示 worker 自动选；auto_start_port 控制扫描起点
# 配合 --network=host 直接生效；bridge 模式需要在 docker run 时映射 42505-42605:42505-42605
CMD ["--host=0.0.0.0", "--port=none", "--auto_start_port=42505"]
