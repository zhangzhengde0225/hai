# 更新日志

+ 2025.12.20 v1.3.2 新增worker配置项is_free，用于指示模型是否免费使用，默认为True。如果设置为False，需要管理员在控制台配置模型的定价策略。
+ 2025.12.18 v1.3.1 worker支持dashboard配置啟用和禁用。
+ 2025.12.17 v1.3.0 Worker支持metadata字段，用于支持中枢-边缘智能体协同。
+ 2025.12.16 v1.2.19 修复HaiMCP导入BUG 
+ 2025.12.16 v1.2.18 新增HaiMCP，继承FastMCP，可快速将现有MCP服务封装为HepAI Worker，具体见`examples/remote_model/mcp_to_worker.py`中的示例代码。
+ 2025.12.13 v1.2.17 修复openai_api的bridge.py中非类（Type）的支持问题。
+ 2025.12.02 v1.2.16 修复openai_api的bridge.py中对Any类型的支持
+ 2025.11.24 v1.2.15 LLMRemoteWorker支持了/rerank模型
+ 2025.10.01 v1.2.14 worker支持了mcp，可以通过在HModelConfig中添加`mcp_enabled=True`来启用mcp协议，具体见`hepai/components/haiddf/worker/mcp_adapter`中的示例代码。
+ 2025.09.27 v1.2.13 zzd修复了LLMRemoteModel中embeddings接口重复model参数报错的bug。
+ 2025.09.25 v1.2.13 hmf修复了非流式访问阿里云模型报错的bug。
+ 2025.09.23 v1.2.12 新增mcp_adapter，现在HModelConfig添加`mcp_enabled`参数后，可以通过MCP协议调用worker中的方法，具体见`hepai/components/haiddf/worker/mcp_adapter`中的示例代码。
+ 2025.09.18 v1.2.11 更新了部署云模型的文档、示例代码和一些接口。
+ 2025.09.17 v1.2.9, v1.2.10 修复openai bridge支持openai>=1.109的问题；支持LRModel.get_info(refresh=True)来刷新worker和模型信息。
+ 2025.09.15 v1.2.8 修复了_llm_remote_model.py中anthropic模型流式输出的问题。
+ 2025.09.12 v1.2.7 修复worker_index.html打包时不上传的问题
+ 2025.09.11 v1.2.5, v1.2.6 修复了anthropic模型无法使用的bug(llm_remote_model中anthropic的base_url错误), 修复worker_permissions中owner必须是单个字符串的bug。
+ 2025.09.10 v1.2.2, v1.2.3, v1.2.4 修复llm_router的bug，修复worker_app中模型初始化的bug，
+ 2025.09.10 v1.2.1 s1_worker.py支持ScienceOne三个磐石模型
+ 2025.09.09 v1.2.0 大版本更新。
    - HepAI Worker支持了监控面板，启动后访问 http://localhost:42602 即可查看Worker的实时状态。
    - HepAI Worker性能提升，大幅度降低延迟；一个worker即可支持数百并发。
    - HepAI Worker支持了Anthropic的同步和异步客户端。
    - 弃用了hepai_object，基本永久解决了与OpenAI包冲突的问题。
+ 2025.07.30 v1.1.40 支持List Agents, agents = client.agents.list()
+ 2025.07.24 v1.1.39 支持anthropic的API，支持从HepAI Client中直接使用Anthropic模型。
+ 2025.07.12 v1.1.38 更新Hai-ECS v3，支持ink专属秘钥验证，保证安全性。
+ 2025.07.06 v1.1.37 将复杂依赖项从`requirements.txt`中移除，改为在`setup.py`中定义。现在可以通过`pip install hepai[full]`来安装所有依赖。
+ 2025.06.16 v1.1.36 修复config_file默认加载错误的任务
+ 2025.06.10 v1.1.35 修复RemoteModel由文件系统产生的bug
+ 2025.04.27 v1.1.34 支持原opendrsai智能体与多智能体协作框架，将from drsai 改为 from hepai.agents即可，具体见 https://code.ihep.ac.cn/hepai/drsai。修复了hai.LLM.chat()方法的bug。
+ 2025.04.25 v1.1.33 支持agents，from hepai.agents import AssistantAgent
+ 2025.04.22 v1.1.32 更新HepAI Client，支持openai 1.75.0，不再使用本地openai文件，支持pydantic>=2.11
+ 2025.04.01 v1.1.31 fix bug，自动安装pydantic版本2.10，如果高于2.11会报错
+ 2025.03.17 v1.1.30 HWorkerAPP现在可传入Fastapi的参数了。
+ 2025.02.22 v1.1.29 适配openai v1.60.0
+ 2025.02.18 v1.1.27 支持deepseek worker
+ 2025.02.14 v1.1.26 client支持`fetch_api_key`方法。
+ 2025.02.11 v1.1.25 更新基础APIKeyInfo类，增加了`app_group`字段
+ 2025.02.10 v1.1.24 升级同步和异步的worker，在test中增加了同步和异步的demo
+ 2025.02.06 v1.1.22 更新HepAI Client，支持异步客户端AsyncClient
+ 2025.01.23 v1.1.21 修复from hepai import Stream Bug
+ 2024.12.31 v1.1.20 更新HepAI Client，支持httpx>=0.28.1
+ 2024.12.26 v1.1.19 添加了verify_api_key方法，适配了DDF1 和 DDF2的api_key验证。
+ 2024.12.22 v1.1.15 更新HepAI remote model
+ 2024.09.29 v1.1.11 更新hepai_object, 支持OpenAI v1.50.2的retries_taken参数
+ 2024.07.01 v1.1.10 更新HepAI client，支持验证api_key，client.verify_api_key(api_key=api_key)
+ 2024.05.18 v1.1.9 更新HepAI client，适配OpenAI 1.30.1，允许传入`stream_options`参数
+ 2024.04.30 v1.1.8 添加Worker支持传入自定义路由，hepai.worker.start(..., extra_routes=[APIRoute(...), ...])
+ 2024.04.25 v1.1.7 Fix text/event-stream parse error in HepAI Client. 提供HepAI Client的[文档](hepai_client.md)。
+ 2024.04.22 v1.1.6 更新Worker，从unified_gate中衍生出chat_completions，用于对话生成任务
+ 2024.04.18 v1.1.4 更新Worker和对应的Client，适配各种返回值：int, float, str, list, dict, pdf, image, txt, stream
+ 2024.04.13 v1.1.3 更新HepAI Worker，现在支持无限函数了，需搭配hepai-ddf>-1.0.4
+ 2024.04.09 v1.1.1 更新HepAI Client
+ 2024.03.08 v1.0.19 删除imp包，支持python3.12
+ 2023.10.18 v1.0.18 接入openai/dalle3模型，parse_args_into_dataclasses方法创建短名parse_args
+ 2023.10.11 v1.0.17，解除worker按ctrl+c退出时心跳子进程不退出的bug，新增退出时向controller发送退出信号的功能。

### 2023.05.18
+ 新增了`hai.worker.start()`方法，可以在代码中快速启动worker。

+ 2023.06.28 v1.0.13, 新增hai.parse_args_into_dataclasses方法来快速解析由dataclasses修饰的类参数。

