from typing import Union
import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

from openai import OpenAI
from hepai import HepAI, ChatCompletion, Stream

# proxy = "http://192.168.32.148:8118"
# base_url = "https://api.openai.com/v1"
# api_key = os.getenv("OPENAI_API_KEY")
# model = "gpt-3.5-turbo"

proxy = None
base_url = "https://aiapi.ihep.ac.cn/v1"
api_key = os.getenv("HEPAI_API_KEY")
model = "lmsys/vicuna-7b"

stream = True

# client = OpenAI(
client = HepAI(
    api_key=api_key,
    base_url=base_url,
    proxy=proxy,
)

completion: Union[ChatCompletion, Stream] = client.chat.completions.create(
  model=model,
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! who are you"}
  ],
  stream=stream,
)

print(completion)
for chunk in completion:
  print(chunk.choices[0].delta)