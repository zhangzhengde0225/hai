

# NPU服务器

目前有一台测试用华为NPU服务器可用，如需使用请联系zdzhang@ihep.ac.cn。


## 服务器介绍

华为Atlas800-9000NPU训练服务器
配置表：
|类型|描述|
|:---|:---|
|机框基础配置|Atlas 800 (Model 9000)(3*2.5"NVME SSD 风冷机箱,4*Kunpeng 920,8*Ascend 910 B)|
|CPU|192核 （Kunpeng 920 2.6GHz * 4）|
|内存|768G （32G 2933MHz * 24）|
|NPU卡|128G显存（Ascend 910 B * 8）|
|硬盘2|NVME 1.92TB SSD|
|网卡1|板载GE电口|
|网卡2|TM272板载灵活网卡-100GE-2端口-QSFP28|
|电源|8000W （服务器白金2000W * 4）|


安装位置：多学科机房
IP：192.168.68.22（内网）
系统：Centos 8.2
软件：Pytorch 1.8.1+ascend


## 服务器使用
指令：
```bash
# 登录
ssh -p22 <your_account>@192.168.68.22
# 输入你的密码

# 登录后
npu-smi info  # 查看显卡信息
htop  # 查看cpu信息
df -h  # 查看硬盘信息
passwd  # 修改自己的用户密码

# 系统python安装路径：/usr/local/python3.7.5
python  # 打开python
>>> import torch
>>> torch.__version__  # 查看torch版本
或可以自行安装，安装包在根目录：/software

# 用系统自带python运行demo
cp /software/demo.py ~
python demo.py
```

## 注意事项

当前阶段(2023.01~)为测试阶段，采用直连主机的形式抢先体验，未来计划采用k8s管理，使用时请注意以下事项：

  * 由于用户共用所有NPU卡，单个用户最多同时使用1~2张卡，以免影响其他用户使用。
  * 请注意服务器升级信息，如有升级，可能会影响服务器使用，如有影响，会提前通知。