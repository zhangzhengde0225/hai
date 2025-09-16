from hepai import HRModel
import os
from hepai.tools.get_woker_functions import get_worker_sync_functions, get_worker_async_functions

api_key = os.environ.get("HEPAI_API_KEY")
funcs_decs = get_worker_sync_functions(name="hepai/custom-model", api_key=api_key)
print([f.__name__ for f in funcs_decs])

print(funcs_decs[0]())
print(funcs_decs[1]())