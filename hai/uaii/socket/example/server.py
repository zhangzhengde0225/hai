import eventlet
import socketio

debug = False
sio = socketio.Server(logger=debug, engineio_logger=debug)
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


@sio.event
def connect(sid, environ):
    print('connect ', sid)
    print('environ', environ)


@sio.event
def my_message(sid, data):
    print(f'my_message received message: {data}')


@sio.event
def server_run_func(sid, data):
    print(f'server run_func, data: {data}')
    return 'dame', 'dame2'


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
