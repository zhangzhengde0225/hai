# 更新日志


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

