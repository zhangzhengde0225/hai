#!/bin/bash
# 一键构建 HepAI LLM Worker 镜像
# 可在任意目录下执行；版本号自动从 hai/version.py（hepai.__version__ 的字面源头）读取
# 用法：
#   bash hepai/workers/llm_worker/build.sh                # 在仓库根
#   cd hepai/workers/llm_worker && bash build.sh         # 在 worker 目录
#   IMAGE_TAG=dev bash build.sh                          # 显式指定 tag
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# 从 hai/version.py 抽取 __version__，hepai/__init__.py 通过 `from hai import __version__` 暴露的就是它
VERSION_FILE="$REPO_ROOT/hai/version.py"
if [[ ! -f "$VERSION_FILE" ]]; then
    echo "[build] Error: version file not found: $VERSION_FILE" >&2
    exit 1
fi
AUTO_VERSION=$(grep -E "^__version__\s*=" "$VERSION_FILE" \
    | head -n1 \
    | sed -E "s/.*=\s*['\"]([^'\"]+)['\"].*/\1/")
if [[ -z "$AUTO_VERSION" ]]; then
    echo "[build] Error: cannot parse __version__ from $VERSION_FILE" >&2
    exit 1
fi

IMAGE_NAME="${IMAGE_NAME:-hepai-llm-worker}"
IMAGE_TAG="${IMAGE_TAG:-$AUTO_VERSION}"
# 是否同步打 latest 标签（默认开启；设为 0 关闭）
TAG_LATEST="${TAG_LATEST:-1}"

cd "$REPO_ROOT"
echo "[build] context   : $REPO_ROOT"
echo "[build] version   : $AUTO_VERSION  (from hai/version.py)"
echo "[build] image     : ${IMAGE_NAME}:${IMAGE_TAG}"
[[ "$TAG_LATEST" == "1" ]] && echo "[build] also tag  : ${IMAGE_NAME}:latest"
echo "[build] dockerfile: hepai/workers/llm_worker/Dockerfile"

extra_tag_args=()
if [[ "$TAG_LATEST" == "1" && "$IMAGE_TAG" != "latest" ]]; then
    extra_tag_args+=(-t "${IMAGE_NAME}:latest")
fi

docker build \
    -f hepai/workers/llm_worker/Dockerfile \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    "${extra_tag_args[@]}" \
    "$@" \
    .

echo "[build] done -> ${IMAGE_NAME}:${IMAGE_TAG}"
