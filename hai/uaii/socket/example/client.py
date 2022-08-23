import os
import time
import socketio

debug = False
sio = socketio.Client(logger=debug, engineio_logger=debug)


@sio.event
def connect():
    print('connection established')


@sio.event
def on_process(*args):
    print(f'on process: {len(args)} args: {args}')
    return args


@sio.event
def my_message(data):
    print('client 收到my_massage函数:', data)
    sio.emit('server_run_func', {'response': data}, callback=on_process)
    return 'xx'


@sio.event
def disconnect():
    print('disconnected from server')


# sio.connect('http://localhost:5000')
sio.connect('http://127.0.0.1:5000')

for i in range(10):
    data = {'a': f'{i}'}
    ret = my_message(data)
    print(f'ret: {ret}')
    time.sleep(0.5)

sio.wait()
