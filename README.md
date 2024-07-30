[![Stars](https://img.shields.io/github/stars/zhangzhengde0225/CDNet)](
https://github.com/zhangzhengde0225/hai)
[![Open issue](https://img.shields.io/github/issues/zhangzhengde0225/CDNet)](
https://github.com/zhangzhengde0225/hai/issues)
<!-- [![Datasets](https://img.shields.io/static/v1?label=Download&message=datasets&color=green)](
https://github.com/zhangzhengde0225/CDNet/blob/master/docs/DATASETS.md)
[![Datasets](https://img.shields.io/static/v1?label=Download&message=source_code&color=orange)](
https://github.com/zhangzhengde0225/CDNet/archive/refs/heads/master.zip) -->

#### English | [简体中文](https://github.com/zhangzhengde0225/hai/blob/main/docs/readme_zh_cn.md)

# HepAI Library
This is [HepAI](https://ai.ihep.ac.cn) python library, the AI platform can accelerate scientific research in multidisciplinary scenarios, simplify model iteration and flow, and is a common infrastructure for the development of AI algorithms and applications.

The HepAI platform itself is a software system that carries AI algorithm models, provides AI computing power, connects data channels, and conducts AI training.

The HepAI framework integrates classic and state-of-the-art (SOTA) artificial intelligence algorithms in the field of high-energy physics. One can access related algorithm models, datasets, and computational resources through a unified interface, making the application of AI simple and efficient.

<details open>
<summary><b>News</b></summary>

+ [2024.05.16] v1.1.9 HepAI Client支持GPT-4o, 调用方法:
+ [2024.03.26] v1.0.21 Make LLM request like OpenAI via HepAI object.
+ [2023.10.24] v1.0.18 接入dalle文生图模型，调用方法教程见[此处](https://note.ihep.ac.cn/s/EG60U1Rtf)。
+ [2023.04.21] v1.0.7通过hepai使用GPT-3.5，[hepai_api.md](docs/hepai_api.md).
+ [2023.02.09] 基于ChatGPT的**HaiChatGPT**已上线，使用简单，无需梯子！详情查看：[HaiChatGPT](https://code.ihep.ac.cn/zdzhang/haichatgpt).
+ [2023.01.16] 华为NPU服务器上架，如有算法国产化需求，请查阅[NPU文档](docs/computing_power/npu_power_doc.md)。
+ [2022.10.20] HAI v1.0.6-Beta 第一个测试版本发布，4个算法和3个数据集
+ [2022.08.23] HAI v1.0.0
</details>

<details open>
<summary><b>Tutorials</b></summary>

[Quick Start to Using HepAI on Computing Clusters](docs/quickstart_hpc.md)

[Reconstruction and identification of atmospheric neutrinos in JUNO experiments using PointNet](https://code.ihep.ac.cn/zhangyiyu/pointnet)

</details>

<details open>
<summary><b>Algorithm Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/model_zoo.md">
    <ul>
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=4 online, 3 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=天体物理&message=1 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=同步辐射&message=2 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=中子物理&message=0">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=通用神经网络&message=2 online, 5 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=经典机器学习&message=TODO">
    </ul>
    </a>
    
</details>

<details open>
<summary><b>Dataset Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/datasets.md">
<ul>
<li>
    <img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=3 available, 10+ TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=CV&message=1 available">
    </a>
</details>


### Quick start
```
pip install hepai --upgrade
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
    或其他支持gRPC的语言，详见[deploy](docs/deploy.md)


not