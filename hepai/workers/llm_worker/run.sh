#!/bin/bash
# 一键启动 HepAI LLM Worker 容器
#
# 常用环境变量（在命令前 KEY=VAL 临时覆盖即可）：
#   IMAGE_NAME           镜像名，默认 hepai-llm-worker
#   IMAGE_TAG            镜像标签，默认 latest
#   CONTAINER_NAME       容器名，默认 hepai-llm-worker
#   HOST_PORT            宿主端口，默认 42505
#   CONTAINER_PORT       容器内端口，默认 42505
#   ENV_FILE             .env 文件路径，默认仓库根 .env
#   CONTROLLER_ADDRESS   controller 地址，默认 http://host.docker.internal:42501
#   WORKER_NAME          worker_name 覆盖（可选）
#
# 任何额外参数会原样追加到 llm_worker.py 后面，例如：
#   bash run.sh --no-register=true --enable_llm_router=false
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

IMAGE_NAME="${IMAGE_NAME:-hepai-llm-worker}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-hepai-llm-worker}"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"

# 网络模式：
#   host    - 与宿主机共享网络栈（推荐，支持 worker 自动选端口；仅 Linux）
#   bridge  - 默认 docker 网络，需要明确 -p 映射端口
NETWORK_MODE="${NETWORK_MODE:-host}"

# bridge 模式专用：宿主-容器端口映射
HOST_PORT="${HOST_PORT:-42505}"
CONTAINER_PORT="${CONTAINER_PORT:-42505}"

# host 模式下，controller 就是宿主机的 localhost；bridge 模式经 host.docker.internal
if [[ "$NETWORK_MODE" == "host" ]]; then
    CONTROLLER_ADDRESS="${CONTROLLER_ADDRESS:-http://localhost:42501}"
else
    CONTROLLER_ADDRESS="${CONTROLLER_ADDRESS:-http://host.docker.internal:42501}"
fi

# 端口参数：none = 让 worker 自动选；--port=42505 = 指定
# 默认 none（配合 host 网络可直接生效）
WORKER_PORT="${WORKER_PORT:-auto}"
# 自动选端口时的起始扫描端口
AUTO_START_PORT="${AUTO_START_PORT:-42602}"

env_file_args=()
if [[ -f "$ENV_FILE" ]]; then
    env_file_args=(--env-file "$ENV_FILE")
    echo "[run] env-file   : $ENV_FILE"
else
    echo "[run] env-file   : (not found, skipped) $ENV_FILE"
fi

extra_worker_args=()
if [[ -n "${WORKER_NAME:-}" ]]; then
    extra_worker_args+=(--worker_name="$WORKER_NAME")
fi

# 前置校验：worker_name 必填（环境变量 WORKER_NAME 或直接在 $@ 中显式传 --worker_name=）
has_worker_name_arg=0
for arg in "$@"; do
    case "$arg" in
        --worker_name=*|--worker_name) has_worker_name_arg=1 ;;
    esac
done
if [[ -z "${WORKER_NAME:-}" && $has_worker_name_arg -eq 0 ]]; then
    cat >&2 <<'EOF'
[run.sh] Error: worker_name is required.
  Use one of:
    WORKER_NAME=my_worker bash run.sh
    bash run.sh --worker_name=my_worker
EOF
    exit 2
fi

echo "[run] image      : ${IMAGE_NAME}:${IMAGE_TAG}"
echo "[run] container  : $CONTAINER_NAME"
echo "[run] network    : $NETWORK_MODE"
echo "[run] port       : $WORKER_PORT (auto_start=$AUTO_START_PORT)"
echo "[run] controller : $CONTROLLER_ADDRESS"

network_args=()
if [[ "$NETWORK_MODE" == "host" ]]; then
    network_args=(--network=host)
else
    network_args=(-p "${HOST_PORT}:${CONTAINER_PORT}" --add-host=host.docker.internal:host-gateway)
fi

exec docker run --rm \
    --name "$CONTAINER_NAME" \
    "${network_args[@]}" \
    "${env_file_args[@]}" \
    "${IMAGE_NAME}:${IMAGE_TAG}" \
    --host=0.0.0.0 \
    --port="$WORKER_PORT" \
    --auto_start_port="$AUTO_START_PORT" \
    --controller_address="$CONTROLLER_ADDRESS" \
    "${extra_worker_args[@]}" \
    "$@"
