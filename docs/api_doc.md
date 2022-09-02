

# gRPC API
使用gRPC把xai封装成一个服务，可实现跨语言调用。

ip: localhost (default: 192.168.30.99)
port: 9999 (default: 9999)

## 开启xai服务的方法
进入xai安装的主机(例如：192.168.30.99)的命令行终端，执行以下命令：
```shell
xai-server start   # 在默认的9999端口，以安全TLS加密方式开启xai服务

# 参数
start|stop|restart  # 必选参数，开启、关闭或重启xai服务，
--insecure  # 以不安全连接的方式启动，即无TLS加密验证，例如：xai-server start --insecure
-p 或 --port  # 指定端口号，例如：xai-server start -p 9999
```
启动方法：进入/home/user/PycharmProject/xsensing目录，执行：```bash ./run_xai_server.sh```

## Python实现客户端和调用函数

获取grpc, xai_pb2, xai_pb2_grpc的方法：
[技术实践：教你用Python搭建gRPC服务](https://zhuanlan.zhihu.com/p/384953226)
，其中后两个包需要自定义xai.proto后用grpcio-tools生成。

服务端启动后，客户端调用方法如下：
```python
import grpc
import xai_pb2, xai_pb2_grpc

# 1. 获取客户端
ip = 'localhost'  # 或指定地址
port = 50052 
conn = grpc.insecure_channel(f'{ip}:{port}')
client = xai_pb2_grpc.GrpcServiceStub(channel=conn)  # 获取客户端

# 2. 调用方法
func = 'xxx'  # 函数名，需要调用的xai的函数，字符串类型
params = {'xxx': 'xxx'}  # 参数，dict，类似于Json
params_bytes = str(params).encode('utf-8')  # 转为bytes
request = xai_pb2.CallRequest(func=func, params=params_bytes)  # 生成请求体
response = client.call(request)  # 调用xai的函数，返回响应体，类型是string

# 3. python调用示例

```
如例所示，调用函数的方法是调用call函数
请求体CallReqeust的格式为：
request.func: string类型，指定需要调用的函数名
request.params: json_string编码后的bytes类型，指定被调用函数的参数，服务端接收收解码

响应体的格式为：
response.status：int类型，1是成功, 其他是错误，其中：0是警告，-1是错误
response.data：bytes类型，可能由string, json_string, int等数据类型编码而来，查阅下表可知各函数的响应数据类型

## 可用的func和params
| 函数名func | 参数params       | 说明                                                 | 响应数据类型      |
|---|----------------|----------------------------------------------------|-------------|
| ps      | 空{}           | 返回xai所有的模块、I/O、脚本和工作流                              | string or json列表 |
|build_stream| 流配置项：type, models | 构建新的工作流，返回工作流的名字                                   | string      |
|get_stream_info| 流名stream_name  | 返回流的信息，包括流的名字、模型、输入、输出、工作流等信息                      | string      |
|get_stream_cfg| 流名stream_name，地址addr | 读取工作流的配置，返回json字符串                                 | json字典      |
|set_stream_cfg| 流名stream_name，地址addr，新配置new_cfg | 设置工作流的配置，返回新的配置                                    | json字典      |
|get_stream_cfg_meta| 流名stream_name，地址addr | 读取工作流的配置的元数据，包含每个参数的默认值、描述、类型、是否固定、取值范围等，返回json字符串 | json字典      |
|run_stream| 流名stream_name, 任务task | 运行工作流，返回工作流的名字                                     | string      |

TODO: 暂停流，停止流。

## 详细参数说明
### ps()
无必选参数
```python
params = dict(
    ret_fmt='string',  # 可选参数，指定返回的数据格式，默认：'string'，可选'json'
    stream=False,  # 可选参数，如果为True，则只返回stream类型的ps数据
    module=False,  # 可选参数，如果为True，则只返回module类型的ps数据
    io=False,  # 可选参数，如果为True，则只返回io类型的ps数据
    script=False,  # 可选参数，如果为True，则只返回script类型的ps数据
    type=None,  # 可选参数，如果为None，则返回所有类型的ps数据，如果为'module'，则返回module类型的ps数据，以此类推
)
```

### build_stream()
python字典json键值对，格式是流配置格式

stream_config的配置文件格式如下：
```python
vis_stream_config = dict(
            type='vis_stream',  # 必选参数，指定新流的名字
            models=[   # 必选参数，指定新流内包含的模块，list类型，有前后顺序
                dict(
                    type='seyolov5',),  # 至少一个模块，type指定模块的名字
                dict(
                    type='deepsort',  # 第二个模块，
                    cfg='/path/to/deepsort/deepsort_cfg.py'),  # 可带配置文件，如果有，初始化时会用这个配置文件与默认配置文件合并
                ])
```

### get_stream_info()
返回流的信息，包括流的名字、模型、输入、输出、工作流等信息
参数：
```python
params = dict(
    ret_fmt='string',  # 可选参数，指定返回的数据格式，默认：'string'，可选'json', 'dict'
    stream_name='vis_stream',  # 必选参数，指定流名
)
```

#### 一个典型的流的信息
```
            class : <class "Stream">  # 流对象的类
             name : test_stream  # 流的名字
      description : 测试创建的工作流  # 流的描述
           status : stopped  # 流当前的状态
          is_mono : True  # 流是否是mono的，只包含1个算法模型的是mono
           models : (1)  # 包含的算法模型，list
                  m02 : seyolov5  # 包含的第1个算法模型的id和名字
  seyolov5 config : (5)  # 第1个算法模型的配置信息
                model : (10)  # 关于模型的配置
                     type : SEYOLOv5
                   device : 0
                  weights : ./weights/yolov5s.weights
                     half : True
                  augment : False
                   use_se : False
                 backnone : None
                     neck : None
                     head : None
                    names : ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
         input_stream : (3)  # 关于输入的配置
                     type : visible_input
                   source : /home/user/datasets/xsensing/mm_data/slice_P4_1217/vis
                 img_size : 640
         post_process : (3)  # 关于输出的配置
                     type : yolov5 post process
                      nms : (3)
                   conf_thres : 0.25
                    iou_thres : 0.45
                 agnostic_nms : False
             filt_classes : (2)
                      enabled : True
                valid_classes : ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 'chair', 'bed']
        output_stream : (6)  # 关于输出的配置
                     type : default_yolov5_output
                 save_dir : None
                 save_txt : False
                save_conf : False
                print_ret : True
                      que : (3)
                      enabled : True
                       maxlen : 5
                         wait : False
                train : (3)
                optimizer : (1)
                         type : Adam
              max_epoches : 100
                  augment : True
```

### get_stream_status()
获取已存在的算法流的状态，可能的值有：stopped, running, ready

参数：流名
```python
params = dict(
    stream_name='vis_stream',  # 必选参数，指定流名
)
```

### get_stream_cfg()
构建新的工作流，返回工作流的名字 

参数：流名，地址

```python
params = dict(
    stream_name='vis_stream',   # 必选参数，指定流的名字
    addr='/',  # 可选参数，读取的配置地址，默认值是/，代表流的所有配置，addr='/seyolov5'，代表这个流的seyolov5的配置，以此类推
    
)
```
其中addr的默认值是/，代表这个流的根目录，即vis_stream的所有配置
addr='/seyolov5'，代表这个流的seyolov5的配置

### get_stream_cfg_meta()
读取工作流的配置的元数据，包含每个参数的默认值、描述、类型、是否固定、取值范围等

参数：
```python
params = dict(
    stream_name='vis_stream',  # 流名
    addr='/',  # 地址
    )
```

### set_stream_cfg()
设置工作流的配置，返回新的配置

参数：
```python
params = dict(
    stream_name='vis_stream',  # 流名
    addr='/',  # 地址
    cfg=new_cfg)  # 修改后的配置，json格式，可通过get_stream_cfg获取，自定义修改后获取
```
