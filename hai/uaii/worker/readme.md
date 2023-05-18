

分布式部署worker的相关函数

用法：
1. 启动一个worker，worker与controller通信，接收controller的指令，执行指令
2. 向worker中添加模型即可

### 使用方法：

```
import hai
hai.worker.start(
    model=model,
    host="0.0.0.0",
    port="auto",
    controller_address="https://chat.ihep.ac.cn",
    worker_address="auto",
    limit_model_concurrency=5,
    stream_interval=0.,
    no_register=False,
    premissions="group: all"
)
```

参数：
```
model  # 模型，需要有inference和train等方法，接收**kwargs参数
host: str = "0.0.0.0"  # worker的地址，0.0.0.0表示外部可访问，127.0.0.1表示只有本机可访问
port: str = "auto"  # 默认从42902开始
controller_address: str = "http://chat.ihep.ac.cn:42901"  # 控制器的地址
worker_address: str = "auto"  # 默认是http://<ip>:<port>
limit_model_concurrency: int = 5  # 限制模型的并发请求
stream_interval: float = 0.  # 额外的流式响应间隔
no_register: bool = False  # 不注册到控制器
premissions: str = 'group: all'  # 模型的权限授予，分为用户和组，用;分隔
```


#### Deprecated

```
hai worker start --host 0.0.0.0 \
    --port auto \
    --controller_address http://chat.ihep.ac.cn:42901 \
    --worker_address auto \
    --worker_address: str = "auto" \
    --limit_model_concurrency: int = 5 \
    --stream_interval 0. \
    --premissions "group: all"
```





