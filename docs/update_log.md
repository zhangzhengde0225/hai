# 更新日志

+ 2024.04.13 v1.1.3 更新HepAI Worker，现在支持无限函数了，需搭配hepai-ddf>-1.0.4
+ 2024.04.09 v1.1.1 更新HepAI Client
+ 2024.03.08 v1.0.19 删除imp包，支持python3.12
+ 2023.10.18 v1.0.18 接入openai/dalle3模型，parse_args_into_dataclasses方法创建短名parse_args
+ 2023.10.11 v1.0.17，解除worker按ctrl+c退出时心跳子进程不退出的bug，新增退出时向controller发送退出信号的功能。

### 2023.05.18
+ 新增了`hai.worker.start()`方法，可以在代码中快速启动worker。

+ 2023.06.28 v1.0.13, 新增hai.parse_args_into_dataclasses方法来快速解析由dataclasses修饰的类参数。

