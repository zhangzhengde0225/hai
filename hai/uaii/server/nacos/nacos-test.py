
import os
import sys

import damei as dm

from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent
# sys.path.append(f'{pydir.parent.parent.parent.parent}/nacos-sdk-python')
from xsensing_ai.uaii.server.nacos import nacos

# Both HTTP/HTTPS protocols are supported, if not set protocol prefix default is HTTP, and HTTPS with no ssl check
# (verify=False)
# "192.168.3.4:8848" or "https://192.168.3.4:443" or "http://192.168.3.4:8848,192.168.3.5:8848" or
# "https://192.168.3.4:443,https://192.168.3.5:443"
SERVER_ADDRESSES = "192.169.30.101:8848"
NAMESPACE = "nacos.naming.serviceName"
username = None
password = None

# 实例化客户端
client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username="nacos", password="nacos")
client.set_debugging()

# get config
# data_id = "config.nacos"
# group = "group"
# print(client.get_config(data_id, group))

# 创建服务
# curl -X POST '192.168.30.101:8848/nacos/v1/ns/service?serviceName=ai-service&metadata=k1%3dv1'

# 查询服务
code = "curl -X GET '192.168.30.101:8848/nacos/v1/ns/service/list?pageNo=1&pageSize=10'"
ret = dm.popen(code)
ret = eval(ret[-1].strip())

print(ret, len(ret), type(ret))
doms = ret["doms"]
if 'ai-service' not in doms:
    reg_code = "curl -X POST '192.168.30.101:8848/nacos/v1/ns/service?serviceName=ai-service&metadata=k1%3dv1'"
    os.system(reg_code)
    ret = eval(dm.popen(code)[-1].strip())
    print(ret)

# 往服务里注册实例
client.add_naming_instance(
    service_name="ai-service",
    ip="192.168.30.101",
    port=8848,
)

