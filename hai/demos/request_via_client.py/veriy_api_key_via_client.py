from typing import Union, Dict
import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__
from hai.configs import CONST

from hepai import HepAI, ChatCompletion, Stream

# base_url = "https://api.openai.com/v1"
# base_url = "http://localhost:42901/v1"
base_url = "https://aiapi.ihep.ac.cn/v1"

client = HepAI(api_key=os.getenv("HEPAI_API_KEY"), base_url=base_url, max_retries=0)

api_key = os.getenv("HEPAI_API_KEY")
rst: Dict = client.verify_api_key(api_key=api_key)

if not rst["success"]:
    print(f"API key verification failed. Info:\n {rst}")
else:
    print(f"API key verification success. Info:\n {rst}")
