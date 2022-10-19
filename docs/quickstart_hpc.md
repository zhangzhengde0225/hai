
## 在计算集群上使用HAI的快速入门

高能物理AI平台(HAI)分为算法框架、模型库、数据集、算力资源四个部分。其中，HAI算法框架集成高能物理领域经典和SOTA的算法，提供统一、简单、易用的复现和应用接口。

本教程主要介绍在高能所计算集群上使用HAI的快速入门，即如何使用HAI算法框架对已集成的算法进行模型训练、评估和推理。

## 开始之前

### 环境配置
+ 登录集群并添加换环境变量
    ```bash
    ssh <account>@lxslc7.ihep.ac.cn  
    # 添加HAI环境变量
    export PATH="/cvmfs/hai.ihep.ac.cn/bin:$PATH"  # 执行或添加到.bashrc，并source ~/.bashrc
    ```
    HAI算法框架已通过cvmfs发布，运行算法所需python, pytorch等依赖已经可以直接使用。如需自行安装，执行`pip install hepai`或参考[安装文档](docs/install.md)。

+ 创建工作目录
    ```bash
    mkdir workspace
    cd workspace
    ```

## 开始

```bash
hai --version  # 查看HAI当前版本
hai list  # 列出本地已安装的算法
```
查看更多支持的算法并下载：
```bash
hai list remote  # 查看已发布的算法
hai download <algorithm_name>  # 下载算法到本地, 例如：hai download particle_transformer
```
下载后，算法源码会被克隆到当前目录的`<algorithm_name>`文件夹内。
```bash
cd particle_transformer

python train.py  # 训练模型
```
train.py内通过hai调用模型的接口简单、统一：
    
```python
import hai

model_name = 'particle_transformer'
model = hai.hub.load(model_name)  # 加载模型对象，其他模型同理
config = model.config  # 获取模型参数
config.source = "xxx"  # 修改source配置，指定数据集，其他参数同理
model.train()  # 训练模型
```
更多算法模型请参考[模型库](docs/model_zoo.md)。

更多使用教程请参考[教程](docs/tutorial.md)。







