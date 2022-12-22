#!/home/user/anaconda3/envs/xsensing/bin/python
# coding: utf-8
"""
基于gRPC封装的hai, 提供服务端, 客户端可跨语言是实现调用
usage:
    python hai-server.py
    hai start server
"""
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent
sys.path.append(f'{pydir.parent}')
# import hai

import argparse
import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent
sys.path.append(f'{pydir.parent}')
# import hai
from hai.uaii.server import run as run_server

def get_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='start', help='start|stop|restart mode')
    parser.add_argument('--insecure', action='store_true', help='use secure grpc or insecure grpc')
    parser.add_argument('-p', '--port', type=int, default=9999, help='port to listen on')
    parser.add_argument('--debug', '-d', default=True, action='store_true', help='debug mode')
    return parser.parse_args()

if __name__ == '__main__':
    opt = get_opt()
    run_server(opt)
