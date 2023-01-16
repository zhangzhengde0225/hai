# [HAI](https://code.ihep.ac.cn/zdzhang/hai)
高能物理AI平台(HAI)分为算法框架、模型库、数据集、算力资源四个部分。其中，HAI算法框架集成高能物理领域经典和SOTA的人工智能算法，提供统一、简单、易用的复现和应用接口。

<details open>
<summary><b>News</b></summary>

+ [2023.01.16] 华为NPU服务器上架，如有算法国产化需求，请查阅[NPU文档](docs/computing_power/npu_power_doc.md)。
+ [2022.10.20] HAI v1.0.6-Beta 第一个测试版本发布，4个算法和3个数据集

+ [2022.08.23] HAI v1.0.0
</details>

<details open>
<summary><b>Tutorials</b></summary>

[在计算集群上使用HAI的快速入门](docs/quickstart_hpc.md)

[使用PointNet对JUNO实验的大气中微子进行重建和鉴别](https://code.ihep.ac.cn/zhangyiyu/pointnet)

更多教程[TODO]

</details>

<details open>
<summary><b>Algorithm Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/model_zoo.md">
<img src="https://img.shields.io/static/v1?style=social&label=图像相关&message=2 online, 5 TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=分类算法&message=3 TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=4 online, 3 TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=天体物理&message=1 TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=射线科学&message=3 TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=机器学习&message=TODO">
    </a>
    
</details>

<details open>
<summary><b>Dataset Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/datasets.md">
<img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=3 available, 10+ TODO">
    <br>
    <img src="https://img.shields.io/static/v1?style=social&label=CV&message=1 available">
    </a>
</details>


### Quick start
```
pip install hepai
hai -V  # 查看版本
```

1. 命令行使用

    ```bash
    hai train <model_name>  # 训练模型, 例如: hai train particle_transformer
    hai eval <model_name>
    ```

2. python库使用

    python库统一接口：
    ```python
    import hai
    
    model = hai.hub.load('<model_name>')  # 加载模型
    config = model.config  # 获取模型配置
    config.batch_size = 32  # 修改配置
    model.trian()  # 训练模型
    model.eval()  # 评估模型
    model.infer('<data>')  # 模型推理
    hai.train('particle_transformer')
    ```

3. 部署和远程调用

    跨语言、跨平台的模型部署和远程调用

    服务端：
    ```bash
    hai start server  # 启动服务
    ```
    客户端
    ```bash
    pip install hai-client
    ```
    ```python
    import hai_client
    hai = hai_client.HAI()
    ```
    或其他支持gRPC的语言，详见[deploy](docs/deploy.md)（TODO）


### TODO
+ Visualize the dataset
  +  .parquet file
    + images

+ Display in the docker container




