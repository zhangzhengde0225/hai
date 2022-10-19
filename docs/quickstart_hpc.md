
# 在计算集群上使用HAI的快速入门

高能物理AI平台(HAI)分为算法框架、模型库、数据集、算力资源四个部分。其中，HAI算法框架集成高能物理领域经典和SOTA的算法，提供统一、简单、易用的复现和应用接口。

本教程以粒子物理用于喷注分类的4个算法和3个数据集为例，主要介绍如何在高能所计算集群上使用HAI对已集成的算法进行模型训练、评估和推理。

# 1. 一次性准备工作

## 1.1 登录集群
```bash
ssh <account>@lxslc7.ihep.ac.cn  
```
## 1.2 安装hai和配置运行环境
+ 使用已部署环境变量

    HAI算法框架已通过cvmfs发布，添加环境变量后hai软件及其所需python, pytorch等依赖已集成，可以直接使用。
    ```bash
    # 添加HAI环境变量
    source /cvmfs/hai.ihep.ac.cn/envs/hai_env/bin/activate
    ```
+ 或者 快速拷贝环境变量
    ```bash
    cp -r /cvmfs/hai.ihep.ac.cn/envs/hai_env .  # 拷贝
    source hai_env/bin/activate  # 添加环境变量
    ```
+ 或者 自行安装hai和配置环境变量
    运行`pip install hepai`并参考[安装文档](docs/install.md)安装依赖项。

## 1.3 创建工作目录
```bash
mkdir workspace
cd workspace
```

## 1.4 准备算法代码
```bash
hai --version  # 查看HAI当前版本
```

```bash
hai list  # 列出本地已安装的算法
hai list remote  # 查看更多支持的算法
hai download <algorithm_name>  # 下载算法到本地, 例如：hai download particle_transformer
```
下载后，算法源码会被克隆到当前目录的`<algorithm_name>`文件夹内。
```bash
cd particle_transformer
hai list  # 已下载的算法也会被列出，如不在算法文件夹内将不会注册
```

## 1.5 关于数据集（Optianal）
集群上允许无需下载数据集，HAI已发布的数据集暂存于/hepsfs/user/zdzhang/hai_datasets下，公开数据集所有人均有全部权限。
如需下载，可执行：
```bash
hai list datasets  # 列出本地数据集
hai list remote datasets  # 查看更多支持的数据集
hai download datasets <dataset_name>  # 下载数据集到本地, 例如：hai download datasets QuarkGluon
```

# 2. 开始

## 2.1 训练模型
```bash
python train.py  # 训练模型
```
train.py内通过hai调用模型的接口简单、统一：
    
```python
import hai

model_name = 'particle_transformer'
model = hai.hub.load(model_name)  # 加载算法对象，其他模型同理
config = model.config  # 获取模型配置
config.source = "xxx"  # 修改参数source，指定数据集，其他参数同理
config.weights = "xxx"  # 指定预训练模型
print(config)  # 打印所有配置(包括默认配置)
model.train()  # 训练模型
```

可通过`python train.py --h`查看更多参数，可选参数：
```bash
    [-n --name <model name>]  # 模型名：可选： Particle_Transformer(默认), ParticleNet, PCNN, Particle_Flow_Network
    [-s --source <input dataset>]  # 输入源，即数据集名称，可选：QuakGluon(默认), JetClass, TopLandscape
    [-f --feature_type <feature_type>]  # 输入模型所使用的特征类型，可选：full(默认), kin, kinpid
```
+ note:
    + kin: only kinematic inputs
    + kinpid: kinematic inputs + particle identification
    + <b>full (default)</b>: kinematic inputs + particle identification + trajectory displacement


训练中，可以通过控制台输出的网址查看训练过程。
训练结束后，模型和训练日志将保存着在runs文件夹内。


# 说明

HAI算法框架搜集和集成优秀算法，是介于最顶层应用和Pytorch, Tesnflow、PaddlePaddl等人工智能框架的中间件。

作为算法开发者，您无需基于HAI开发算法（我们也不提供底层的算子），您可以基于任何人工智能框架和算力硬件开发算法，开发完成后我们通过一套hai_api即可快速集成您的算法，从而实现统一复现和应用API。HAI算法框架对于您来说是一个用于横向对比的“算法仓库”和“数据集仓库”，也是一个“算法发布平台”。

作为算法使用者，您可以通过HAI快速实现算法的使用、测试、部署。

更多算法模型请参考[算法库](docs/algorithm_zoo.md)。

更多数据集请参考[数据集](docs/datasets.md)。

更多使用教程请参考[教程](docs/tutorial.md)。


## TODO:
+ 从codo.ihpe.ac.cn下载算法，需要账号，同步开源到github
+ 评估、推理、部署




