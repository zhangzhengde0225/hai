"""
测试
"""

# ! /usr/bin/env python
# coding=utf8
import os, sys
from pathlib import Path
import grpc
from grpc import ssl_server_credentials
import time
import damei as dm
from concurrent import futures

pydir = Path(os.path.abspath(__file__)).parent
sys.path.append(f'{pydir}')
import xai_pb2_grpc, xai_pb2
sys.path.remove(f'{pydir}')
import xsensing_ai as xai


logger = dm.getLogger('xai_server')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class XAIService(xai_pb2_grpc.GrpcServiceServicer):
    '''
    继承GrpcServiceServicer,实现hello方法
    '''

    def __init__(self):
        self.uaii = xai.UAII()

    def hello(self, request, context):
        '''
        具体实现hello的方法，并按照pb的返回对象构造HelloResponse返回
        :param request:
        :param context: 是保留字段，不用管
        :return:
        '''
        # logger.info(f'hello request: {request}')
        logger.info(f'grpc func "hello" is called.')
        result = request.data + request.skill.name + " this is gprc test service"
        list_result = {"12": 1232}
        return xai_pb2.HelloResponse(result=str(result),
                                     map_result=list_result)

    def call(self, request, context):
        func = request.func

        # 把google.protobuf.xx。ScalarMapContainer转换成dict
        # 弃用，原因是该方法支持map传参，但map传参不支持多种数据类型，必须指定一种类型
        # params = dict(request.params)

        # 处理bytes传参，传是的一个Json字典
        params = request.params
        try:
            params = eval(params.decode('utf-8'))
        except:
            params = params.decode('utf-8')
        params = dict(params)
        # params = dict(eval(params.decode('utf-8')))  # 解析后是一个dict
        # print(params, type(params))

        logger.info(f'grpc func "call" is called. func_name: "{func}", params: {params}')
        status, data = self._call(func, params)
        data = str(data).encode('utf-8')
        return xai_pb2.CallResponse(status=status, data=data)

    def _call(self, func, params):
        """
        实际调用的方法
        :param func: 函数名
        :param params: 参数
        :return: status 和 data
        """
        try:
            if func == 'ps':
                res = self.uaii.ps(**params)
                s = 1
                data = res
            elif func == "build_stream":
                print(params)
                s, data = self.uaii.build_stream(cfg=params, is_req=True)  # 返回的res是stream对象
            elif func == "get_stream_info":
                stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
                s, data = self.uaii.get_stream_info(stream=stream_name, is_req=True, **params)
            elif func == "get_stream_cfg":
                stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
                addr = params.pop('addr', '/')  # 可选参数
                s, data = self.uaii.get_stream_cfg(stream=stream_name, addr=addr, is_req=True, **params)
            elif func == 'set_stream_cfg':
                stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
                addr = params.pop('addr', '/')  # 可选参数
                cfg = params.pop('cfg', params['cfg'])  # 必选参数
                s, data = self.uaii.set_stream_cfg(stream=stream_name, addr=addr, cfg=cfg, is_req=True, **params)
            elif func == "start_stream":
                stream_name = params.pop('stream_name', params['stream_name'])
                s, data = self.uaii.start_stream(stream=stream_name, is_req=True, **params)  # 返回的res是stream对象
            else:
                raise Exception(f'Call func: "{func}" is not supported.')
            return s, data
        except KeyError as e:
            logger.error(f'Call func: "{func}" params failed. KeyError: {e}')
            return -1, f'Call func: "{func}" params failed. KeyError: {e}'
        except NotImplementedError as e:
            logger.error(f'Call func: "{func}" params failed. NotImplementedError: {e}')
            return -1, f'Call func: "{func}" params failed. NotImplementedError: {e}'
        except Exception as e:
            logger.error(f'Call func: "{func}" failed. Exception: {e}')
            return -1, f'Call func: "{func}" failed. Exception: {e}'


def run(ip='localhost', port=50052):
    '''
    模拟服务启动
    :return:
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    xai_pb2_grpc.add_GrpcServiceServicer_to_server(XAIService(), server)
    # address = f'localhost:{port}'
    address = f'{ip}:{port}'
    # server.add_insecure_port(f'[::]:{port}')
    server.add_insecure_port(address)
    server.start()
    # print("start service...")
    logger.info(f"Service is started at {address} ...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def run_secure(port=50052):
    """开启安全的服务端"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    xai_pb2_grpc.add_GrpcServiceServicer_to_server(XAIService(), server)



def run_debug():
    from xsensing_ai.uaii.server.grpc.grpc_xai_client import XAIGrpcClient
    client = XAIGrpcClient('localhost', 50052)
    # response = client.hello()
    # print("received:", response.result, response.map_result)
    response = client.__call__()
    print(f'call的返回结果：{response.result}')


if __name__ == '__main__':
    run(port=10086)
