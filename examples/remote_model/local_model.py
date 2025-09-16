
import os
# try:
#     import os
#     from hepai import __version__
# except:
#     import os, sys
#     from pathlib import Path
#     here = Path(__file__).parent
#     sys.path.insert(1, str(here.parent.parent))
#     from hepai import __version__


from hepai import HRModel

model = HRModel.connect(
    api_key=os.getenv("HEPAI_API_KEY", ""),
    name="hepai/custom-model",
    # base_url="http://localhost:4260/apiv2"
    # base_url="http://localhost:42601/apiv2"
    base_url="https://aiapi.ihep.ac.cn/apiv2"
)

funcs = model.functions  # Get all remote callable functions.
print(f"Remote callable funcs: {funcs}")

# 请求远程模型的custom_method方法
output = model.custom_method(a=1, b=2)
assert isinstance(output, int), f"output: type: {type(output)}, {output}"
print(f"Output of custon_method: {output}, type: {type(output)}")

stream = model.get_stream(stream=True)  # Note: You should set `stream=True` to get a stream.
print(f"Output of get_stream:")
for x in stream:
    print(f"{x}, type: {type(x)}", flush=True)
    

info = model.get_info()  # Get model info.
print(f"Model info: {info}, type: {type(info)}")
