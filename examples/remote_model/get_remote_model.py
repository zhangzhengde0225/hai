

try:
    from hepai import __version__
except:
    import os, sys
    from pathlib import Path
    here = Path(__file__).parent
    sys.path.insert(1, str(here.parent.parent))
    from hepai import __version__



from hepai import HepAI, LRModel

# from hepai.types import HRemoteModel

# 创建HepAI客户端
client = HepAI(base_url="http://localhost:4260/apiv2")

# 获取一个远程模型对象
model_name = "hepai/custom-model"
model: LRModel = client.get_remote_model(model_name=model_name)

print(model.get_info())  # 获取模型资源信息

# 请求远程模型的custom_method方法
output = model.custom_method(a=1, b=2)
assert isinstance(output, int), f"output: type: {type(output)}, {output}"
print(f"output: {output}")