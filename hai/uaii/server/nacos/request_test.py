
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import ssl

data = {'ip': '192.168.30.101', 'port': 8848, 'serviceName': 'ai-service', 'weight': 1.0, 'enable': True, 'healthy': True, 'clusterName': None, 'ephemeral': True, 'groupName': 'DEFAULT_GROUP', 'namespaceId': 'nacos.naming.serviceName'}
# data = None
server_url = 'http://192.169.30.101:8848'
url = '/nacos/v1/ns/instance?username=nacos&password=nacos'
url = '/nacos/v1/ns/instance'
url = "/nacos/v1/ns/instance?port=8848&healthy=true&ip=11.11.11.11&weight=1.0&serviceName=ai-service&encoding=GBK&namespaceId=n1'"
all_headers = {}
method = 'POST'



req = Request(url=server_url + url, data=urlencode(data).encode() if data else None,
              headers=all_headers, method=method)
# req = Request(url=se)
get_instances_list = 'http://192.168.30.101:8848/nacos/v1/ns/instance/list?serviceName=ai-service'
get_service_list = 'http://192.168.30.101:8848/nacos/v1/ns/service/list?pageNo=1&pageSize=10'
add_service = 'http://192.168.30.101:8848/nacos/v1/ns/service?serviceName=ai-service&metadata=k1%3dv1'
add_instance = f'http://192.168.30.101:8848/nacos/v1/ns/instance?port=8848&healthy=true&ip=11.11.11.11' \
               f'&weight=1.0&serviceName=ai-service&encoding=GBK&namespaceId=n1'


def do(_url, method='GET'):
    req = Request(url=_url, method=method, headers=all_headers,
                  data=urlencode(data).encode() if data else None)
    ctx = ssl.SSLContext()
    timeout = 3
    resp = urlopen(req, timeout=timeout, context=ctx)
    print(resp.read().decode())

print('查询实例列表')
do(get_instances_list)
do(get_service_list)
try:
    do(add_service, method='POST')
    do(get_service_list)
except:
    pass

print('注册实例')
# add_instance = f'http://192.168.30.101:8848/nacos/v1/ns/instance?port=50052&healthy=true&ip=192.168.30.99' \
#                f'&weight=1.0&serviceName=ai-service&encoding=GBK&namespaceId=n1'
add_instance = f'http://192.168.30.101:8848/nacos/v1/ns/instance?port=50052&ip=192.168.30.99&serviceName=ai-service' \
               # f''
do(add_instance, method='POST')
print('查询实例列表')
do(get_instances_list)
print('查询实例详情')
get_instance_detail = f'http://192.168.30.101:8848/nacos/v1/ns/instance?' \
                      f'serviceName=ai-service&ip=192.168.30.99&port=50052&cluster=DEFAULT'
do(get_instance_detail)
