# HepAI LLM Worker —— Docker 一键启动

将 `llm_worker.py` 打包成基于 `python:3.12-slim` 的轻量镜像，配合脚本一键构建与运行。

## 目录结构

```
hepai/workers/llm_worker/
├── Dockerfile        # 镜像构建定义
├── build.sh          # 一键构建脚本
├── run.sh            # 一键运行脚本
├── llm_worker.py     # Worker 入口
└── README.md         # 本文件
```

构建上下文是 **仓库根目录**，因为 `hepai/__init__.py` 里有 `from hai import *`，镜像需要同时包含 `hai/` 与 `hepai/` 两个包。仓库根的 `.dockerignore` 已经排除 `data/`、`repos/`、`docs/`、各类 `node_modules` 等无关内容（裁掉约 300MB+）。

## 一、构建镜像

`build.sh` **可以在任意目录下执行**（脚本会自己定位仓库根作为构建上下文），版本号自动从 `hai/version.py`（也就是 `hepai.__version__` 的字面源头）读取作为镜像 tag。

```bash
# 在仓库根目录
bash hepai/workers/llm_worker/build.sh

# 或者切到 worker 目录直接跑
cd hepai/workers/llm_worker
bash build.sh
```

默认会同时打两个 tag：`hepai-llm-worker:{version}` 和 `hepai-llm-worker:latest`，例如版本是 `1.4.2.1` 时：

```
hepai-llm-worker:1.4.2.1
hepai-llm-worker:latest
```

自定义镜像名 / 标签：

```bash
# 覆盖镜像名
IMAGE_NAME=my-llm-worker bash hepai/workers/llm_worker/build.sh

# 显式指定 tag（覆盖自动版本）
IMAGE_TAG=dev bash hepai/workers/llm_worker/build.sh

# 不要同步打 latest
TAG_LATEST=0 bash hepai/workers/llm_worker/build.sh
```

向 `docker build` 透传额外参数（例如禁用缓存、指定平台）：

```bash
bash hepai/workers/llm_worker/build.sh --no-cache
bash hepai/workers/llm_worker/build.sh --platform=linux/amd64
```

构建期主要分两层：

1. `pip install -r requirements.txt` —— 依赖层，源码改动不会触发重装。
2. `COPY hai/ hepai/` —— 源码层，改动 worker 代码只需重建本层。

## 二、运行容器

最简（自动读取仓库根 `.env`，自动经 `host.docker.internal` 访问宿主机 controller）：

```bash
# worker_name 是必填项
WORKER_NAME=my_worker bash hepai/workers/llm_worker/run.sh
# 或
bash hepai/workers/llm_worker/run.sh --worker_name=my_worker
```

等价的原始命令：

```bash
docker run --rm \
    --name hepai-llm-worker \
    -p 42505:42505 \
    --env-file .env \
    --add-host=host.docker.internal:host-gateway \
    hepai-llm-worker:latest \
    --host=0.0.0.0 \
    --port=42505 \
    --controller_address=http://host.docker.internal:42501
```

### 常用环境变量

`run.sh` 通过环境变量参数化，直接在命令前 `KEY=VAL` 临时覆盖即可：

| 变量                 | 默认值                                  | 说明                                      |
| -------------------- | --------------------------------------- | ----------------------------------------- |
| `IMAGE_NAME`         | `hepai-llm-worker`                      | 镜像名                                    |
| `IMAGE_TAG`          | `latest`                                | 镜像标签                                  |
| `CONTAINER_NAME`     | `hepai-llm-worker`                      | 容器名                                    |
| `HOST_PORT`          | `42505`                                 | 宿主机端口                                |
| `CONTAINER_PORT`     | `42505`                                 | 容器内监听端口                            |
| `ENV_FILE`           | 仓库根 `.env`                           | 注入到容器的 env file 路径                |
| `CONTROLLER_ADDRESS` | `http://host.docker.internal:42501`     | controller 地址                           |
| `WORKER_NAME`        | **(必填)**                              | worker 标识；决定 controller 注册名 和 `~/.hepai/worker_configs/{worker_name}.json` 路径。未设置且未在命令行传 `--worker_name=` 时启动会立即报错 |

示例：

```bash
# 连远程 controller
CONTROLLER_ADDRESS=https://aiapi.ihep.ac.cn bash hepai/workers/llm_worker/run.sh

# 自定义 worker 名 + 宿主端口
WORKER_NAME=my_worker HOST_PORT=52505 bash hepai/workers/llm_worker/run.sh

# 指定其他 .env 文件
ENV_FILE=/path/to/prod.env bash hepai/workers/llm_worker/run.sh
```

### 透传任意 worker 参数

`run.sh` 末尾的 `"$@"` 会把剩余参数原样追加到 `llm_worker.py` 后面，等同于直接给 `python llm_worker.py` 传参：

```bash
bash hepai/workers/llm_worker/run.sh \
    --no-register=true \
    --enable_llm_router=false \
    --limit_model_concurrency=200
```

可用参数请看 `llm_worker.py` 里的 `WorkerConfig` dataclass 字段。

## 三、`.env` 与机密管理

- `.env` **不打进镜像**，运行时通过 `--env-file` 注入到容器进程环境；`.dockerignore` 已将 `.env` 排除在构建上下文之外。
- `llm_worker.py` 中的 `load_dotenv()` 在容器里找不到 `.env` 文件也无害，因为变量已经在 `os.environ` 里。
- 生产环境建议使用 `docker run --env KEY=VAL ...` 或 secret 管理工具，而不是把 `.env` 复制到服务器上。

## 四、常见问题

**Q: 容器里连不上宿主机的 controller？**
Linux 默认没有 `host.docker.internal`。`run.sh` 已经加了 `--add-host=host.docker.internal:host-gateway`，可直接用。若手动 `docker run`，记得带上同样的参数；或改用 `--network=host`。

**Q: 我改了 `hepai/` 下的源码，要重新构建吗？**
要。`COPY` 只在构建时生效。开发期想热更新，可在 `docker run` 时加 `-v $(pwd)/hepai:/app/hepai -v $(pwd)/hai:/app/hai` 把本地源码挂进去。

**Q: 镜像里有 `pip install`，但 controller 地址默认是 `localhost`，启动时没传 `--controller_address` 会怎样？**
会尝试连接容器内的 `localhost:42501`，几乎一定失败。`run.sh` 已经强制传了 `--controller_address`，用 docker run 直跑时务必显式指定。

**Q: 构建上下文太大、`docker build` 卡在 sending context？**
检查仓库根 `.dockerignore` 是否生效（应当裁掉 `data/`、`repos/`、所有 `node_modules` 等）。可执行 `du -sh .` 确认总量。

## 五、镜像清单

- 基础镜像：`python:3.12-slim`
- 运行时依赖：`requirements.txt`（fastapi / uvicorn / openai / anthropic / mcp / ...）
- 入口：`python /app/hepai/workers/llm_worker/llm_worker.py`
- 默认 CMD：`--host=0.0.0.0 --port=42505`
- 暴露端口：`42505`
