

from typing import Optional
import platform
import uuid
import os
import hashlib
import random
import ast
import json
from fastapi.requests import Request


    
def get_uuid(lenth, prefix=None):
    import uuid
    if prefix:
        return prefix + str(uuid.uuid4())[:lenth-len(prefix)]
    return str(uuid.uuid4())[:lenth]

def gen_one_id(lenth, prefix='wk-', extra_indicators: Optional[list] = None) -> str:
    """
    在相同的机器、相同的用户、相同的模型名称时，生成相同的id
    """
    indentifiers = get_simple_machine_indicator()
    if extra_indicators:
        indentifiers.extend(extra_indicators)
    # namespace_dns = uuid.NAMESPACE_DNS
    uuid_v5 = uuid.uuid5(
        namespace=uuid.NAMESPACE_DNS,
        name='-'.join(indentifiers)
    )
    if prefix:
        gened_id = prefix + str(uuid_v5)[:lenth-len(prefix)]
    else:
        gened_id = str(uuid_v5)[:lenth]
    return gened_id

def get_hostname():
    import socket
    return socket.gethostname()


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
    if port == 'auto' or port is None or port == 0:
        # 获取所有被占用的端口号
        used_ports = get_used_ports(start=start, **kwargs)
        for i in range(start, 65535):
            if i not in used_ports:
                return int(i)
        raise ValueError('No available port')
    else:
        return port
    

def _get_all_interface_ips():
    """获取所有网卡的 (接口名, IP) 列表，排除 loopback"""
    import socket, struct, fcntl, array

    result = []
    # 使用 SIOCGIFCONF 枚举所有网卡
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 分配足够大的缓冲区
        buf = array.array('B', b'\0' * 4096)
        # struct ifreq 在 Linux 上是 40 字节
        ifconf = struct.pack('iL', 4096, buf.buffer_info()[0])
        result_bytes = fcntl.ioctl(s.fileno(), 0x8912, ifconf)  # SIOCGIFCONF
        size = struct.unpack('iL', result_bytes)[0]
        data = buf.tobytes()[:size]

        offset = 0
        while offset < size:
            ifname = data[offset:offset+16].split(b'\0', 1)[0].decode()
            ip_bytes = data[offset+20:offset+24]
            ip = socket.inet_ntoa(ip_bytes)
            offset += 40  # sizeof(struct ifreq) on Linux

            if ip.startswith('127.'):
                continue
            result.append((ifname, ip))
    finally:
        s.close()
    return result


def _detect_best_ip():
    """
    智能选择本机 IP:
    1. 环境变量 WORKER_IP 优先（手动覆盖）
    2. 在 K8s 环境中有多个网卡时，优先选非 eth0 的接口
       （eth0 通常是 K8s CNI 分配的 pod 网络，net1 等是 Multus/macvlan 分配的）
    3. 只有一个网卡时直接使用
    4. 兜底：UDP socket 默认路由
    """
    import os, socket

    # 1. 环境变量手动覆盖
    env_ip = os.environ.get("WORKER_IP")
    if env_ip:
        return env_ip

    # 2. 枚举网卡，智能选择
    try:
        interfaces = _get_all_interface_ips()
    except Exception:
        interfaces = []

    if len(interfaces) == 1:
        return interfaces[0][1]

    if len(interfaces) > 1:
        # K8s 环境检测：存在 serviceaccount 目录
        is_k8s = os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount")
        if is_k8s:
            # 优先选非 eth0 的接口（macvlan / SR-IOV 等由 Multus 注入的额外网卡）
            non_eth0 = [(name, ip) for name, ip in interfaces if name != "eth0"]
            if non_eth0:
                chosen_name, chosen_ip = non_eth0[0]
                import logging
                # logging.getLogger("worker_utils").info(
                #     f"K8s detected with multiple interfaces, chose {chosen_name}({chosen_ip}) over eth0"
                # )
                return chosen_ip

    # 3. 兜底：UDP socket 默认路由
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]


def auto_worker_address(worker_address, host, port):
    if worker_address != 'auto':
        return worker_address
    if host in ['localhost', '127.0.0.1']:
        return f'http://{host}:{port}'
    elif host == '0.0.0.0':
        ip = _detect_best_ip()
        return f'http://{ip}:{port}'
    else:
        raise ValueError(f'host {host} is not supported')


def extract_worker_id(text: str) -> str:
    import re
    # 使用正则表达式来匹配格式形如 'wk-xxxx-xxxx' 的 worker_id
    # match = re.search(r'worker_id: `(\w+-\w+)`', text)
    match = re.search(r'worker_id:\s*`([^`]*)`', text)
    if match:
        return match.group(1)
    return None

def wait_for_worker(worker_id, timeout=10):
    # 向服务发起请求
    import os, time
    from haiddf import HaiDDF
    from haiddf._types import WorkerInfo
    client = HaiDDF(api_key=os.getenv("DDF_API_KEY"))

    start_time = time.time()
    while time.time() - start_time < timeout:
        wk_info = client.get_worker_info(worker_id=worker_id)
        if isinstance(wk_info, WorkerInfo):
            return wk_info
        time.sleep(0.5)
    return False

def run_standlone_worker_demo(logger=None):
    import os, sys
    import time
    from pathlib import Path
    here = Path(__file__).parent

    class PrintLogger:
        def info(self, *args, **kwargs):
            print(*args, **kwargs)

    logger = logger or PrintLogger()
    
    current_dir = os.getcwd()

    import subprocess
    from datetime import datetime

    os.chdir(str(here))
    try:
        print(f"Run standalone worker demo in `{here}` ...", end="")
        # logger.info(f"Run standalone worker demo in `{here}` ...")
        ct = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"nohup.out.demo.{ct}"
        cmd = f"nohup python demo_worker.py >{log_file} 2>&1 &"
        result = subprocess.run(
            cmd,
            shell=True,  
            check=True,  # 如果命令失败，抛出 CalledProcessError
            capture_output=True,  # 捕获标准输出和标准错误
            text=True  # 将输出作为字符串处理，而不是字节
        )
        print(", succeeded.", end="")
        # print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(", failed.")
        print("Error message:")
        print(e.stderr)
        raise e

    os.chdir(current_dir)

    # 从logfile读取worker_id
    # 等待worker启动
    time.sleep(0.5)

    # 等待文件被创建和写入
    file_path = f"{here}/{log_file}"
    timeout = 5
    t0 = time.time() 
    while True:
        ct = time.time() - t0
        if ct > timeout:
            raise TimeoutError(f"Wait for worker start timeout. {ct}s")
        if not os.path.exists(file_path):
            time.sleep(0.5)
            # print(f"Waiting for file `{file_path}` to be created ... {ct}s")
            logger.info(f"Waiting for log_file `{log_file}` to be created ... {ct:.2f}s")
            continue
        
        with open(f'{here}/{log_file}', 'r') as f:
            text = f.read()
            if text == "":
                time.sleep(0.5)
                logger.info(f"Waiting for log_file `{log_file}` to be written ... {ct}s")
                # print(f"Waiting for file `{file_path}` to be written ... {ct}s")
                continue
        worker_id = extract_worker_id(text)
        # print(f" Worker_id: `{worker_id}`")
        if worker_id:
            return wait_for_worker(worker_id, timeout=10)
        else:
            if "Traceback" in text:
                chunks = text.split("Traceback")
                error_msg = f"Traceback{chunks[-1]}"
                raise ProcessLookupError(f"Worker started failed. {error_msg}")
            # print(" Worker started, but worker_id not found.")
            # return
            raise ValueError("Worker started, but worker_id not found.")


def get_simple_machine_indicator() -> list:
    # 组合多个系统标识
    identifiers = [
        platform.node(),          # 主机名
        platform.machine(),       # 架构
        str(uuid.getnode()),      # MAC地址
        os.path.expanduser('~'),  # 用户目录路径
    ]
    
    # 添加环境变量中的唯一标识（如果存在）
    env_keys = ['HOSTNAME', 'COMPUTERNAME', 'USER', 'USERNAME']
    for key in env_keys:
        if key in os.environ:
            identifiers.append(os.environ[key])
    return identifiers


def get_simple_machine_seed(extra_indicators: Optional[list] = None) -> int:
    """
    根据机器的标识信息生成一个简单的种子数，可用于随机数生成或其他需要唯一标识的场景。
    机器的标识信息包括主机名、架构、MAC地址、用户目录路径、HOSTNAME、COMPUTERNAME、USER、USERNAME，以及额外的标识信息（如果提供）。
    """
    
    identifiers = get_simple_machine_indicator()
    
    if extra_indicators:
        identifiers.extend(extra_indicators)
    
    # 生成种子
    combined = ''.join(identifiers)
    seed_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    return int(seed_hash[:8], 16)     
        
def gen_one_key(prefix='sk-', lenth=47, seed=None):
    import string
    import time
    # 生成所有可能的字符集合
    all_chars = string.ascii_letters
    
    seed = seed if seed is not None else int(time.time())
    # random.seed(time.time())
    rng = random.Random(seed)
    # 生成47位随机字符串
    random_string = ''.join(rng.choice(all_chars) for _ in range(lenth))
    random_string = f'{prefix}{random_string}'
    # print(random_string)
    return random_string


async def read_request_body(request: Optional[Request]) -> dict:
    """
    Asynchronous function to read the request body and parse it as JSON or literal data.

    Parameters:
    - request: The request object to read the body from

    Returns:
    - dict: Parsed request data as a dictionary
    """
    try:
        request_data: dict = {}
        if request is None:
            return request_data
        body = await request.body()

        if body == b"" or body is None:
            return request_data
        body_str = body.decode()
        try:
            request_data = ast.literal_eval(body_str)
        except:
            request_data = json.loads(body_str)
        return request_data
    except:
        return {}