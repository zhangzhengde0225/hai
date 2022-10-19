#! /usr/bin/env python
# coding=utf8

import grpc
import hello_pb2_grpc, hello_pb2


def run():
    '''
    模拟请求服务方法信息
    :return:
    '''
    conn = grpc.insecure_channel('localhost:50052')
    client = hello_pb2_grpc.GrpcServiceStub(channel=conn)
    skill = hello_pb2.Skill(name="engineer")
    request = hello_pb2.HelloRequest(data="xiao gang", skill=skill)
    respnse = client.hello(request)
    print("received:", respnse.result, respnse.map_result)


if __name__ == '__main__':
    run()
