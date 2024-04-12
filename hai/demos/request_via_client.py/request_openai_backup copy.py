


import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

from typing import cast, Any, Dict, List, Optional, Tuple, Union
import httpx

from openai import OpenAI
from hepai import HepAI

proxy = "http://192.168.32.148:8118"
base_url = "https://api.openai.com/v1"
http_client = httpx.Client(
            base_url=base_url,
            # cast to a valid type because mypy doesn't understand our type narrowing
            timeout=60,
            proxies={
                "http://": proxy,
                "https://": proxy,
            },
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

client = OpenAI(
# client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=base_url,
    http_client=http_client,
    # proxy=proxy,
)

stream = client.chat.completions.create(
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
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
    

