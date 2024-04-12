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

# client = OpenAI(
client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=base_url,
    proxy=proxy,
)

completion: Union[ChatCompletion, Stream] = client.chat.completions.create(
  model="gpt-4-turbo",
  messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "What's in this image?"},
            {
              "type": "image_url",
              "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            },
          ],
        }
    ],
  max_tokens=300,
)

print(completion)
