

def pretty_print_semaphore(semaphore):
    if semaphore is None:
        return "None"
    return f"Semaphore(value={semaphore._value}, locked={semaphore.locked()})"

def get_used_ports(start=1, end=65535):
    import socket
    ports = []
    for port in range(start, end):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
        except:
            ports.append(port)
        finally:
            s.close()
    return ports

def auto_port(port=None, start=42901, **kwargs):
    """
    自动获取端口，返回数字端口号
    """
    if port == 'auto':
        # 获取所有被占用的端口号
        used_ports = get_used_ports(start=start, **kwargs)
        for i in range(start, 65535):
            if i not in used_ports:
                return int(i)
        raise ValueError('No available port')
    else:
        return port
    
def auto_worker_address(worker_address, host, port):
    import socket
    if worker_address != 'auto':
        return worker_address
    if host in ['localhost', '127.0.0.1']:
        return f'http://{host}:{port}'
    elif host == '0.0.0.0':
        ## TODO，此处需要改进，获取本机ip
        # 获取本机的外部 IP 地址是使用一个与外部世界的连接
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        return f'http://{ip}:{port}'
    else:
        raise ValueError(f'host {host} is not supported')


    
