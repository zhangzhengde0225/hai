# 更新日志

+ 2023.10.18 v1.0.18 接入openai/dalle3模型，parse_args_into_dataclasses方法创建短名parse_args
+ 2023.10.11 v1.0.17，解除worker按ctrl+c退出时心跳子进程不退出的bug，新增退出时向controller发送退出信号的功能。

### 2023.05.18
+ 新增了`hai.worker.start()`方法，可以在代码中快速启动worker。

+ 2023.06.28 v1.0.13, 新增hai.parse_args_into_dataclasses方法来快速解析由dataclasses修饰的类参数。