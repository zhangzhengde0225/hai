#!/home/user/anaconda3/envs/xsensing/bin/python
# coding: utf-8
"""
基于gRPC封装的hai, 提供服务端, 客户端可跨语言是实现调用
usage:
    python hai-server.py
"""

import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent
sys.path.append(f'{pydir.parent}')
import hai

from xsensing_ai.uaii.server.grpc import grpc_xai_server_secure
import xsensing_ai
import argparse
import damei as dm

logger = dm.get_logger('xai-server')


def get_is_running(port):
    ret = dm.popen(f'netstat -tanlp')
    ret = [x.split() for x in ret if len(x.split()) == 7]
    # port = str(opt.port)
    ports = [f'{x[3].split(":")[-1]}' for x in ret]
    if port in ports:  # 有正在运行的服务
        index = ports.index(port)
        pid = ret[index][-1]
        if 'python' not in pid:  # 如果不是python进程，则不是xai服务
            logger.warn(f'port {port} is running, but not xai-server')
            return False
        else:
            pid = pid.split('/')[0]
            # dm.popen(f'kill -9 {pid}')
            return pid
    else:
        # logger.error(f'xai-server on port {port} is not running')
        return False


def run(opt):
    # grpc_xai_server.run(ip=ip, port=port)
    logger.info(f'xai version: {xsensing_ai.__version__}')
    logger.info(f'xai-server params: {opt}')
    assert opt.mode in ['start', 'stop', 'restart'], 'mode must be start, stop or restart'
    if opt.mode == 'start':
        if opt.insecure:
            grpc_xai_server_secure.run_insecure(port=opt.port)
        else:
            grpc_xai_server_secure.run(port=opt.port)
    elif opt.mode == 'stop':
        is_running = get_is_running(str(opt.port))
        # print(is_running)
        if is_running:  # 如果有运行的服务，返回的是pid
            dm.popen(f'kill -9 {is_running}')
        else:
            logger.warn(f'xai-server on port {opt.port} is not running')
            sys.exit(0)
    else:
        is_running = get_is_running(str(opt.port))
        if is_running:
            dm.popen(f'kill -9 {is_running}')
        if opt.insecure:
            grpc_xai_server_secure.run_insecure(port=opt.port)
        else:
            grpc_xai_server_secure.run(port=opt.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, default='start', help='start|stop|restart mode')
    parser.add_argument('--insecure', action='store_true', help='use secure grpc or insecure grpc')
    parser.add_argument('-p', '--port', type=int, default=9999, help='port to listen on')

    opt = parser.parse_args()

    run(opt)
