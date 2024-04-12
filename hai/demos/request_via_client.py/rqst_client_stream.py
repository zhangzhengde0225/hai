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

proxy = "http://192.168.32.148:8118"
base_url = "https://api.openai.com/v1"
stream = True

# client = OpenAI(
client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=base_url,
    proxy=proxy,
)

completion: Union[ChatCompletion, Stream] = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  stream=stream,
)

print(completion)
for chunk in completion:
  print(chunk.choices[0].delta)