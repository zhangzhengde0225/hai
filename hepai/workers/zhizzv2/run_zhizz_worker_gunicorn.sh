#!/bin/bash
# 用 gunicorn 启动 llm_worker（多进程模式）
#
# 必填环境变量：
#   WORKER_NAME           worker 唯一标识（用于 controller 注册 和 ~/.hepai/worker_configs/{name}.json）
# 可选环境变量：
#   HOST                  默认 0.0.0.0
#   PORT                  默认 42602（gunicorn 监听端口；同时也传给 worker 内部 config）
#   CONTROLLER_ADDRESS    默认 http://localhost:42501
#   NO_REGISTER           默认 false
#   GUNICORN_WORKERS      gunicorn worker 进程数，默认 4
#
# 用法：
#   WORKER_NAME=openrouter_cn bash run_worker_gunicorn.sh
set -euo pipefail

export WORKER_NAME="${WORKER_NAME:-zhizzv2}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-42602}"
# export CONTROLLER_ADDRESS="${CONTROLLER_ADDRESS:-http://localhost:42501}"
export CONTROLLER_ADDRESS="${CONTROLLER_ADDRESS:-https://aiapi.ihep.ac.cn}"
export NO_REGISTER="${NO_REGISTER:-false}"

GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"

echo "[gunicorn] WORKER_NAME       = $WORKER_NAME"
echo "[gunicorn] bind              = ${HOST}:${PORT}"
echo "[gunicorn] CONTROLLER_ADDRESS= $CONTROLLER_ADDRESS"
echo "[gunicorn] workers           = $GUNICORN_WORKERS"

exec gunicorn -w "$GUNICORN_WORKERS" \
    -k uvicorn.workers.UvicornWorker \
    --bind "${HOST}:${PORT}" \
    "hepai.workers.llm_worker.llm_worker:create_app()"

