# About
高能物理AI算法平台，集成经典和SOTA人工智能算法，提供统一、便捷API接口，自动分配资源，为科学家提供人工智能算法和算力支持。

## TODO：支持的算法模型

### 图像相关
    目标检测算法YOLOv5, SEYOLOv5, YOLOv7
    图像分割算法UNet, TransUNet, SegFormer
    人体关键点检测算法AlphaPose
### 分类算法
    残差网络ResNet
    浅层网络FCNet
    密集连接网络DenseNet
### 物理相关
    费米神经网络Ferminet
    多喷注事例重建算法SPNet
    寻找奇异粒子算法HiggsSusy
    衍射数据幅度和相位预测算法PtychoNN
    相位恢复算法PhaseGAN 有数据集
### 机器学习
    支持向量机SVM
    随机森林Random Forest
    基于树的XGBoost
    滤波方法Deepsort
### 自然语言处理
    Transformer

# 数据集
## 图像相关(1个)
    MSCOCO：目标检测、实例分割、人体关键节点检测数据集
## 物理相关(12个)
    2021_ttbar 多喷注事例重建数据集
    Antihydrogen, htautau, hepjets, HEPMASS, Higgs&SUSY, Jet Flavor, neutrino, 2020_electron, muon_2020, 2021_muon, 2020_SARM 


# TODO
Visualize the dataset
    .parquet file


# Getting Started
```
pip install hepai

hai --version
```



