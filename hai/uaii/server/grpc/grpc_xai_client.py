#! /usr/bin/env python
# coding=utf8
# import logging

# import damei as dm
import grpc
import warnings
import copy
import json

try:
    import damei as dm
except:
    import os, sys
    from pathlib import Path
    pydir = Path(os.path.abspath(__file__)).parent
    sys.path.append(f'{pydir.parent.parent.parent.parent.parent}/damei')
    import damei as dm

try:
    import xai_pb2_grpc, xai_pb2
except:
    import os, sys
    from pathlib import Path
    pydir = Path(os.path.abspath(__file__)).parent
    sys.path.append(f'{pydir}')
    # from xsensing_ai.uaii.server.grpc import xai_pb2_grpc, xai_pb2
    import xai_pb2_grpc, xai_pb2
    sys.path.remove(f'{pydir}')

logger = dm.getLogger('grpc_xai_client')


def run():
    '''
    模拟请求服务方法信息，这个是样例
    :return:
    '''
    conn = grpc.insecure_channel('localhost:50052')
    client = xai_pb2_grpc.GrpcServiceStub(channel=conn)
    skill = xai_pb2.Skill(name="engineer")
    request = xai_pb2.HelloRequest(data="xiao gang", skill=skill)
    respnse = client.hello(request)
    print("Received:", respnse.result, respnse.map_result)


class XAIGrpcClient(object):
    def __init__(self, ip='localhost', port=50052):
        # 初始化客户端
        address = f'{ip}:{port}'
        logger.info(f'Connecting to {address}')
        self.address = address
        conn = grpc.insecure_channel(address)
        self.client = xai_pb2_grpc.GrpcServiceStub(channel=conn)
        self.is_connected()
        # print('xxx', self.client)

    def is_connected(self):
        try:
            s, data = self.__call__(func='ps', params={})
            assert s == 1, data
            # logger.info(f'Connected to {self.address}')
        except Exception as e:
            logger.error(e)
            raise Exception(f'Connect to server "{self.address}" failed, error info: {e}')

    def hello(self):
        """请求服务端hellp函数的方法"""
        skill = xai_pb2.Skill(name="engineer")
        request = xai_pb2.HelloRequest(data='im damei', skill=skill)
        response = self.client.hello(request)
        return response

    def __call__(self, func, params=None, **kwargs):
        """调用服务端的函数"""
        # empty_params = json.dumps(dict())
        # params = params if params else empty_params
        params = params if params else {}
        # 调用xai.ps()函数
        # 构造请求
        # func = 'p
        # params = xai_pb2.Params(key='1', value=5)
        # params = xai_pb2.Params(key={'key': '1', 'value': '1'}, value={'key': 6, 'value': 6})
        # 把parms转为bytes类型

        params = json.dumps(params)  # dict to json str
        # print('params', params, type(params))
        params_bytes = params.encode('utf-8')
        # params_bytes = params.encode('utf-8')
        request = xai_pb2.CallRequest(func=func, params=params_bytes)
        # 调用服务端的函数
        response = self.client.call(request)
        status, data = response.status, response.data

        data = data.decode('utf-8')  # decode into json or str, json是指json_string
        # print('xxx', data, type(data))
        try:
            data = json.loads(data)
        except:  # 加载失败就直接是str
            pass
            # data = data
        # print('xxx', data, type(data))
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
        params = dict(name='vis_stream')
        s, stream_info = self(func='get_stream_info', params=params)
        assert s == 1, stream_info
        # print(stream_info)
        return stream_info

    def test_get_stream_cfg(self):
        params = dict(name='vis_stream', addr='/')
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
    ps_data = client.test_ps()
    print(ps_data)
    # print(ps_data, type(ps_data), len(ps_data))
    stream_name = client.test_build_stream()
    # stream_info = client.test_get_stream_info()
    # stream_cfg = client.test_get_stream_cfg()
    # stream_cfg = client.test_set_stream_cfg()
