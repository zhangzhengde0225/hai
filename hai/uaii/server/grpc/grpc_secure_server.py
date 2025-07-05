"""
带TLCS/SSL认证的GRPC服务器
"""

# ! /usr/bin/env python
# coding=utf8
import os, sys
from pathlib import Path

import time

import damei as dm
# from concurrent import futures
import json

import hai

pydir = Path(os.path.abspath(__file__)).parent

from . import grpc_pb2_grpc
try:
    from . import grpc_pb2
except ImportError:
    pass

logger = dm.getLogger('xai_server')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class XAIService(grpc_pb2_grpc.GrpcServiceServicer):
    '''
    继承GrpcServiceServicer,实现hello方法
    '''

    def __init__(self, debug=False):
        self.uaii = hai.UAII()
        self.debug = debug  # 在debeg模式下，不捕获异常，方便调试，但是错误的调用会导致服务器崩溃

    def hello(self, request, context):
        '''
        具体实现hello的方法，并按照pb的返回对象构造HelloResponse返回
        :param request:
        :param context: 是保留字段，不用管
        :return:
        '''
        # logger.info(f'hello request: {request}')
        logger.info(f'Grpc func "hello" is called.')
        result = request.data + request.skill.name + " this is gprc test service"
        list_result = {"12": 1232}
        return grpc_pb2.HelloResponse(result=str(result),
                                     map_result=list_result)

    def data_reformat(self, data, **kwargs):
        """由于grpc传输的数据类型有限，所以需要对数据进行转换"""
        if data is None:
            return data
        data_type = kwargs.pop('data_type', None)
        if data_type is None or data_type == type(data):
            return data
        import numpy as np
        if data_type in [np.ndarray, 'np.ndarray', 'numpy.ndarray']:
            data = np.array(data)
        else:  # TODO: 支持其他类型数据转换
            raise TypeError(f'data_type "{data_type}" not suported yet.')
        return data

    def data_info(self, data):
        import numpy as np
        if data is None:
            return ''
        elif isinstance(data, np.ndarray):
            return f'data: {data.shape}'
        elif isinstance(data, str):
            return f'data: {data}'
        elif isinstance(data, dict):
            return f'data_keys: {data.keys()}'
        else:
            raise TypeError(f'data type "{type(data)}" not supported yet.')

    def call(self, request, context):
        # 1.处理请求和参数
        func = request.func
       
        params = request.params
        params = params.decode('utf-8')
        params = json.loads(params)
        try:
            params = eval(params)
        except:
            params = params

        data = params.pop('data', None)
        data = self.data_reformat(data, **params)  # 转换数据类型
        
        logger.info(f'Call GPRC "{func}", params: {params} {self.data_info(data)}')

        # 2.调用函数
        status, data = self._call(func, params, data=data)
        logger.info(f'Return: \nStatus: {status} \nData: \n{data} {type(data)}')

        # 3.封装和返回结果
        import numpy as np
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, np.ndarray):
            data = str(data.tolist()).encode('utf-8')
        else:
            # print(status, data, type(data))
            data = str(data).encode('utf-8')
        # print(data, type(data))
        
        return grpc_pb2.CallResponse(status=status, data=data)

    def _call(self, func, params, data=None):
        """
        实际调用的方法
        :param func: 函数名
        :param params: 参数
        :return: status 和 data
        """
        if self.debug:
            # print(f'debug model func: {func}')
            s, data = self.call2(func, params, data=data)
            return s, data
        else:
            try:
                s, data = self.call2(func, params, data=data)
            except KeyError as e:
                e_info = e.__traceback__.tb_frame.f_globals["__file__"] + ":" + str(e.__traceback__.tb_lineno)  # 报错所在文件和行号
                logger.error(f'Call "{func}" params failed. KeyError: {e} in file: {e_info}')
                return -1, f'Call "{func}" params failed. KeyError: {e} in file: {e_info}'
            except NotImplementedError as e:
                e_info = e.__traceback__.tb_frame.f_globals["__file__"] + ":" + str(e.__traceback__.tb_lineno)  # 报错所在文件和行号
                logger.error(f'Call "{func}" params failed. NotImplementedError: {e} in file: {e_info}')
                return -1, f'Call "{func}" params failed. NotImplementedError: {e} in file: {e_info}'
            except Exception as e:
                e_info = e.__traceback__.tb_frame.f_globals["__file__"] + ":" + str(e.__traceback__.tb_lineno)  # 报错所在文件和行号
                logger.error(f'Call "{func}" failed. Exception: {e} in file: {e_info}')
                return -1, f'Call "{func}" failed. Exception: {e} in file: {e_info}'
            return s, data

    def call2(self, func, params, data=None):
        if func == 'ps':
            res = self.uaii.ps(**params)
            s = 1
            data = res
        elif func == "build_stream":
            # print(params, type(params), params.keys())
            s, data = self.uaii.build_stream(cfg=params, is_req=True)  # 返回的res是stream对象
        elif func == "get_stream_info":
            stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
            s, data = self.uaii.get_stream_info(stream=stream_name, is_req=True, **params)
        elif func == "get_stream_cfg":
            stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
            addr = params.pop('addr', '/')  # 可选参数
            s, data = self.uaii.get_stream_cfg(stream=stream_name, addr=addr, is_req=True, **params)
        elif func == "get_stream_cfg_meta":
            stream_name = params.pop('stream_name', params['stream_name'])
            addr = params.pop('addr', '/')
            s, data = self.uaii.get_stream_cfg_meta(stream=stream_name, addr=addr, is_req=True, **params)
        elif func == 'set_stream_cfg':
            stream_name = params.pop('stream_name', params['stream_name'])  # 必选参数
            addr = params.pop('addr', '/')  # 可选参数
            cfg = params.pop('cfg', params['cfg'])  # 必选参数
            # print('xx', cfg, type(cfg))
            if isinstance(cfg, dict):  # 适配python客户端传入dict类型的参数
                pass
            else:
                cfg = json.loads(cfg)  # 适配java客户端传入json类型的参数
            # cfg的类型，可能是
            # if isinstance(cfg, str):
            #     cfg = eval(cfg)  # 兼容客户端调用时候传入的是字符串，需要转换成dict
            # exit()
            s, data = self.uaii.set_stream_cfg(stream=stream_name, addr=addr, cfg=cfg, is_req=True, **params)
        elif func == "start_stream":
            stream_name = params.pop('stream_name', params['stream_name'])
            s, data = self.uaii.start_stream(stream=stream_name, is_req=True, **params)  # 返回的res是stream对象
        elif func == "hub.list":
            s, data = 1, hai.hub.list(**params)
        elif func == "hub.list_weights":
            s, data = 1, hai.hub.list_weights()
        elif func == 'hub.docs':
            s, data = 1, hai.hub.docs(**params)
        elif func == 'hub.load':
            name = params.pop('name', params['name'])
            model = self.uaii.load_model(model_name=name, **params)
            s, data = 1, model.name
        elif func == 'forward':
            s, data = 1, self.uaii.forward(x=data, **params)
        elif func == 'model_config':
            name = params.pop('name', params['name'])
            s, data = 1, self.uaii.model_config(model_name=name, is_req=True, **params)
        elif func == 'set_config':
            name = params.pop('name', params['name'])
            cfg = params.pop('cfg', params['cfg'])
            s, data = 1, self.uaii.set_config(model_name=name, cfg=cfg, is_req=True, **params)
        else:
            raise NotImplementedError(f'Function "{func}" is not supported')
        
        return s, data


def run_insecure(port=50052):
    '''
    模拟服务启动
    :return:
    '''
    import grpc
    from concurrent import futures
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
    ])
    grpc_pb2_grpc.add_GrpcServiceServicer_to_server(XAIService(), server)
    address = f'[::]:{port}'
    server.add_insecure_port(address)
    server.start()
    logger.info(f"Insecure service is started at {address} ...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def run(port=50052, debug=False):
    """开启安全的服务端"""
    import grpc
    from concurrent import futures
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
    ])
    grpc_pb2_grpc.add_GrpcServiceServicer_to_server(XAIService(debug=debug), server)

    # address = f'{ip}:{port}'
    with open(f'{pydir}/cert/server.key', 'rb') as f:
        private_key = f.read()
    with open(f'{pydir}/cert/server.crt', 'rb') as f:
        certificate_chain = f.read()
    server_credentials = grpc.ssl_server_credentials(
        ((private_key, certificate_chain),),)
    address = f'[::]:{port}'
    # address = f'{ip}:{port}'
    # server.add_secure_port(f'[::]:{port}', server_credentials)
    server.add_secure_port(address, server_credentials)
    server.start()
    logger.info(f"Secure service is started at {address} ...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def run_debug():
    from hai.uaii.server.grpc.grpc_xai_client import XAIGrpcClient
    client = XAIGrpcClient('localhost', 50052)
    # response = client.hello()
    # print("received:", response.result, response.map_result)
    response = client.__call__()
    print(f'call的返回结果：{response.result}')


if __name__ == '__main__':
    run(port=10086)
