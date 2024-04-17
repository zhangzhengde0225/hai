
from typing import Any, Dict, List, Tuple, Union
import os, sys
from pathlib import Path
import numpy as np
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

from openai import OpenAI
from hepai import HepAI, HaiFile, Stream

# proxy = "http://192.168.32.148:8118"
# base_url = "https://api.openai.com/v1"
# api_key = os.getenv("OPENAI_API_KEY")
# model = "gpt-3.5-turbo"

proxy = None
# base_url = "http://localhost:42901/v1"
# api_key = os.getenv("HEPAI_A100_API_KEY")
# model = "lmsys/vicuna-7b"

base_url = "https://aiapi.ihep.ac.cn/v1"
api_key = os.getenv("HEPAI_API_KEY")
# model = "lmsys/vicuna-7b"
# model = "lmsys/vicuna-7b-v1.5-16k"
# model = "lmsys/vicuna-13b-v1.5"

# base_url = "http://localhost:42901/v1"
# api_key = os.getenv("HEPAI_3090_API_KEY")
model = "hepai/demo_worker"

# client = OpenAI(
client = HepAI(api_key=api_key, base_url=base_url, proxy=proxy)


test_functions = [
    'get_int', "get_float", "get_bool", "get_str",
    "get_list", "get_dict", "get_image", "get_pdf", "get_stream"]

test_functions_dict = {
    "get_int": int,
    "get_float": float,
    "get_bool": bool,
    "get_str": str,
    "get_list": list,
    "get_dict": dict,
    "get_pdf": HaiFile,
    "get_image": HaiFile,
    # "get_txt": HaiFile,
    'get_stream': Stream,
}

for i, (function, need_type) in enumerate(test_functions_dict.items()):
    stream = function == 'get_stream'
    res: Union[int, float, bool, str, list, HaiFile] = client.request_worker(
        model=model, function=function, stream=stream
        )
    print(f'{function}: {type(res)}')
    assert isinstance(res, need_type), f"Function {function} return type is {type(res)}, not {need_type}"
    if isinstance(res, HaiFile):
        res.save(debug=True)
    elif isinstance(res, Stream):
        for i in res:
            print(f'get_stream: {i} {type(i)}')
    else:
        print(res)

    pass