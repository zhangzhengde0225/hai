import functools
import eventlet
import socketio
import logging
import damei

logger = damei.getLogger('uais_socket')


class SocketApp(object):
    debug = False
    sio = socketio.Server(logger=debug, engineio_logger=debug)
    app = socketio.WSGIApp(sio, static_files={
        '/': {'content_type': 'text/html', 'filename': 'index.html'}})
    uaii = None

    @sio.event
    def connect(sid, environ):
        logger.info(f'客户端连接，sid: {sid}.')
        # print(f'Client connected, sid: {sid}')
        # logger.info(f'Client connected, sid: {sid}')
        # print('environ', environ)

    @sio.event
    def my_message(sid, data):
        print(f'my_message received message: {data}')

    @sio.event
    def server_run_func(sid, data):
        logger.info(f'server run_func, data: {data}')
        # print(f'server run_func, demo_for_dm.data: {demo_for_dm.data}')
        return 'dame', 'dame2'

    @sio.event
    def disconnect(sid):
        logger.info(f'客户端断开连接，sid: {sid}.')
        # print(f'Client disconnected, sid: {sid}')

    @sio.event
    def ps(sid, *args, **kwargs):
        """参数会存在args[0]里"""
        params = args[0]
        # print('客户端让我读取ps信息')
        # params = kwargs.get('params')
        logger.info(f'客户端请求读取ps信息. '
                    # f'sid: {sid} args: {args} kwargs: {kwargs}'
                    )
        ret = SocketApp.uaii.ps()

        return ret

    @sio.event
    def uaii(self, *args):
        """处理来自客户端的uaii请求"""
        print(args)
        func, args, kwargs = args[0][0]
        logger.info(f'收到请求. func: {func} args: {args} **kwargs: {kwargs}')
        if not hasattr(SocketApp.uaii, func):
            logger.error(f'uaii不具有函数：{func}')
        func = getattr(SocketApp.uaii, func)
        # logger.info(f'func: {func} {type(func)}')
        ret = func(*args, **kwargs)

        return ret


def create_socket_app():
    socketapp = SocketApp()
    return socketapp


if __name__ == '__main__':
    app = create_socket_app()
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
