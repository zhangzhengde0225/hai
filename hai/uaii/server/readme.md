这里是xai管理算法作为一个服务，提供接口和对外通信的相关代码


## grpc

```
python -m grpc_tools.protoc -I ./ --python_out=./ --grpc_python_out=. ./hello.proto
```
