from typing import Union
import os, sys
from pathlib import Path
here = Path(__file__).parent
import httpx

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__
from hai.configs import CONST

from openai import OpenAI
from hepai import HepAI, ChatCompletion, Stream

proxy = "http://192.168.32.148:8118"
base_url = "https://api.openai.com/v1"



client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=base_url,
    proxy=proxy,
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=base_url,
    http_client=HepAI().get_http_client(proxy=proxy, base_url=base_url),
)

completion: Union[ChatCompletion, Stream] = client.chat.completions.create(
  model="gpt-4o",
  messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "What's in this image?"},
            {
              "type": "image_url",
              "image_url": {
                  "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                  "detail": "low"
              }
            },
          ],
        }
    ],
  max_tokens=300,
  stream=False,
  # stream_options={"include_usage": True},
)

if isinstance(completion, Stream):
    for message in completion:
        print(message)

print(completion)
