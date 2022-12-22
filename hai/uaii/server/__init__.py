


from .grpc import grpc_secure_server
import argparse
import damei as dm

logger = dm.get_logger('server__init__')


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
    # logger.info(f'xai version: {hai.__version__}')
    logger.info(f'Xai-server params: {opt}')
    assert opt.mode in ['start', 'stop', 'restart'], 'mode must be start, stop or restart'
    if opt.mode == 'start':
        if opt.insecure:
            grpc_secure_server.run_insecure(port=opt.port, debug=opt.debug)
        else:
            grpc_secure_server.run(port=opt.port, debug=opt.debug)
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
            grpc_secure_server.run_insecure(port=opt.port)
        else:
            grpc_secure_server.run(port=opt.port)