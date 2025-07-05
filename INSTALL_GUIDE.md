# HepAI 安装指南

## 基础安装

只安装核心功能所需的基础依赖：

```bash
pip install hepai
```

基础依赖包括：
- damei
- easydict  
- numpy
- pydantic>=2.11.3
- python-dateutil
- httpx>=0.28.1

## 可选功能安装

### 完整安装（所有功能）

```bash
pip install hepai[full]
```

### 按功能模块安装

```bash
# AI 功能（OpenAI 接口等）
pip install hepai[ai]

# 智能体功能
pip install hepai[agents]

# 服务器功能（FastAPI、gRPC等）
pip install hepai[server]

# 图像处理功能
pip install hepai[image]

# 机器学习功能（WandB、进度条等）
pip install hepai[ml]

# Markdown 支持
pip install hepai[markdown]
```

### 组合安装

```bash
# 同时安装多个功能模块
pip install hepai[ai,server,image]
```

## 依赖说明

- **基础依赖**: 提供核心功能，所有安装方式都会包含
- **ai**: OpenAI API 和 token 处理功能
- **agents**: 自动化智能体相关功能  
- **server**: Web 服务器和 API 服务功能
- **image**: 图像处理相关功能
- **ml**: 机器学习实验跟踪和工具
- **markdown**: Markdown 文档处理功能
- **full**: 包含所有上述功能模块
