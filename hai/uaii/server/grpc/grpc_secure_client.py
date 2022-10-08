#! /usr/bin/env python
# coding=utf8
# import logging

# import damei as dm
import grpc
import warnings
import copy
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent

import damei as dm

import grpc_pb2_grpc, grpc_pb2


logger = dm.getLogger('grpc_xai_client')


def run():
    '''
    模拟请求服务方法信息，这个是样例
    :return:
    '''
    conn = grpc.insecure_channel('localhost:50052')
    client = grpc_pb2_grpc.GrpcServiceStub(channel=conn)
    skill = grpc_pb2.Skill(name="engineer")
    request = grpc_pb2.HelloRequest(data="xiao gang", skill=skill)
    respnse = client.hello(request)
    print("Received:", respnse.result, respnse.map_result)


class XAIGrpcClient(object):
    def __init__(self, ip='localhost', port=50052):
        # 初始化客户端
        logger.info('connecting to server: %s:%s', ip, port)
        # conn = grpc.insecure_channel(f'{ip}:{port}')
        with open(f'{pydir}/cert/server.crt', 'rb') as f:
            trusted_certs = f.read()
        credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        channel = grpc.secure_channel(f'{ip}:{port}', credentials, options=[
            ('grpc.ssl_target_name_override', 'ai_service'),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ])
        self.client = grpc_pb2_grpc.GrpcServiceStub(channel=channel)

    def hello(self):
        """请求服务端hellp函数的方法"""
        skill = grpc_pb2.Skill(name="engineer")
        request = grpc_pb2.HelloRequest(data='im damei', skill=skill)
        response = self.client.hello(request)
        return response

    def __call__(self, func, params=None, **kwargs):
        """调用服务端的函数"""
        params = params if params else {}
        # 调用xai.ps()函数
        # 构造请求
        # func = 'p
        # params = xai_pb2.Params(key='1', value=5)
        # params = xai_pb2.Params(key={'key': '1', 'value': '1'}, value={'key': 6, 'value': 6})
        # 把parms转为bytes类型
        params_bytes = str(params).encode('utf-8')
        request = grpc_pb2.CallRequest(func=func, params=params_bytes)
        # 调用服务端的函数
        response = self.client.call(request)
        status, data = response.status, response.data
        try:
            data = eval(data.decode('utf-8'))
        except:
            data = data.decode('utf-8')
        # print('xxxxx', status,)
        if status == -1:
            # raise Exception(data)
            raise Exception(f'{func} error: {data}')
        elif status != 1:
            warnings.warn(f'Function "{func}" call warning, msg：{data}')
        return status, data

    def test_ps(self):
        """测试ps函数"""
        status, ps_data = self(func='ps', params={})
        # print(f'status: {status}, data: {ps_data}')
        assert status == 1, ps_data
        return ps_data

    def test_build_stream(self):
        vis_stream_config = dict(
            type='vis_stream',
            description='测试创建的工作流',
            models=[
                dict(
                    type='seyolov5', )
            ])
        s, new_stream_name = self(func='build_stream', params=vis_stream_config)
        assert s in [0, 1], new_stream_name
        new_stream_name = new_stream_name if s == 1 else new_stream_name.split()[1]  # warn: stream: vis_stream exist，取中间
        s, ps = self(func='ps', params=dict(ret_fmt='list', stream=True))
        stream_names = [x[2] for x in ps[1::]]  # 0行是表头，不需要
        assert new_stream_name in stream_names, f'{new_stream_name} not in {stream_names}'
        return new_stream_name

    def test_get_stream_info(self):
        params = dict(stream_name='vis_stream')
        s, stream_info = self(func='get_stream_info', params=params)
        assert s == 1, stream_info
        # print(stream_info)
        return stream_info

    def test_get_stream_cfg(self):
        params = dict(stream_name='vis_stream', addr='/')
        s, cfg = self(func='get_stream_cfg', params=params)  # 读取流配置文件
        assert s == 1, cfg
        return cfg

    def test_set_stream_cfg(self):
        old_cfg = self.test_get_stream_cfg()
        old_weights = old_cfg['model']['weights']

        # 修改配置
        new_cfg = copy.copy(old_cfg)
        new_cfg['model']['weights'] = './weights/yolov5s.pt'
        print(f'old_weights: {old_weights}')
        print(f'new_weights: {new_cfg["model"]["weights"]}')
        # 设置配置到xai
        params = dict(name='vis_stream', addr='/', cfg=new_cfg)
        s, setted_cfg = self(func='set_stream_cfg', params=params)
        assert s == 1, setted_cfg
        print(s, setted_cfg)

        # stream_info = self.test_get_stream_info()
        # print(stream_info)
        return setted_cfg


if __name__ == '__main__':
    # 示例
    # run()

    # 初始化客户端
    # client = XAIGrpcClient('192.168.30.99', 9999)
    client = XAIGrpcClient('localhost', 9999)
    # client = XAIGrpcClient('127.0.0.1', 9999)
    # client = XAIGrpcClient('192.168.40.133', 9999)
    ps_data = client.test_ps()
    print(ps_data)
    # print(ps_data, type(ps_data), len(ps_data))
    # stream_name = client.test_build_stream()
    # stream_info = client.test_get_stream_info()
    # stream_cfg = client.test_get_stream_cfg()
    # print(stream_cfg)
    # stream_cfg = client.test_set_stream_cfg()
