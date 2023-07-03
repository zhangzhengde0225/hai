

# 通过HepAI部署云端模型的方案

hepai通过controller和workers实现分布式模型部署和负载均衡，
可以将任意一个有`inference`或`train`方法的python对象部署为一个worker。
部署后的worker即可通过hepai的网络接口调用。

## 组件

+ Controller: 控制器，负责管理worker，自动将用户请求分发到空闲的worker
+ Worker: 工作节点，负责处理用户请求
  - WorkerModel: 模型，Worker的一个属性，负责处理用户请求的具体业务逻辑



## 实现

#### 1.安装hepai
```
pip install "hepai>=1.0.13"
```

#### 2.实现代码

`run_worker.py`代码如下：

```python
# (1) 实现WorkerModel
import hai
from hai import BaseWorkerModel
from dataclasses import dataclass, field

class WorkerModel(BaseWorkerModel):
    def __init__(self):
        self.name = "hepai/demo_workermodel"  # name属性用于用于请求指定调研的模型

    @BaseWorkerModel.auto_stream  # 自动将各种类型的输出转为流式输
    def inference(self, **kwargs):
        # 自己的执行逻辑, 例如: # 
        input = 
        output = [1, 2, 3, 4, 5]
        for i in output:
            yield i  # 可以return返回python的基础类型或yield生成器

# (2) worker的参数配置和启动代码

# 启动worker的函数
def run_worker(**kwargs):
    model = WorkerModel()  # 获取模型
    worker_args = hai.parse_args_into_dataclasses(WorkerArgs)  # 解析参数
    # hai.parse_args_into_dataclasses支持多个参数类同时解析，例如：
    # worker_args, model_args = hai.parse_args_into_dataclasses((WorkerArgs, ModelArgs))

    hai.worker.start(
        daemon=False,  # 是否以守护进程的方式启动
        model=model,
        worker_args=worker_args,
        **kwargs
        )


# 用dataclasses修饰器快速定义参数类
@dataclass
class WorkerArgs:
    name: str = "hepai/demo_worker"  # worker的名字
    host: str = "0.0.0.0"  # worker的地址，0.0.0.0表示外部可访问，127.0.0.1表示只有本机可访问
    port: str = "auto"  # 默认从42902开始
    controller_address: str = "http://aiapi.ihep.ac.cn:42901"  # 控制器的地址
    worker_address: str = "auto"  # 默认是http://<ip>:<port>
    limit_model_concurrency: int = 5  # 限制模型的并发请求
    stream_interval: float = 0.  # 额外的流式响应间隔
    no_register: bool = False  # 不注册到控制器
    premissions: str = 'group: all'  # 模型的权限授予，分为用户和组，用;分隔

if __name__ == '__main__':
    run_worker()
```

#### 3.启动worker

`run_worker.sh`如下:

```bash
python run_worker.py \
 --name hepai/demo_worker \
 --controller_address http://aiapi.ihep.ac.cn:42901 \
 --limit_model_concurrency 10 \
 --premissions "group: all"
```

```bash
chmod +x run_worker.sh  # 赋予执行权限
./run_worker.sh  # 启动worker
```

