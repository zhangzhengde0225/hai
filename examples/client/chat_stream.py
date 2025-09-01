



import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, f"{here.parent.parent}")
    from hepai import __version__

from hepai import HepAI
from hepai.types import ChatCompletion, Stream, ChatCompletionChunk



api_key=os.getenv("HEPAI_API_KEY")
base_url = "https://aiapi.ihep.ac.cn/apiv2"
client = HepAI(base_url=base_url, api_key=api_key)

q = "Tell me a short history of Particle Physics"
        
model = "openai/gpt-4o-mini"

stream = True
# 测试非流
print(f"Q: {q}")
rst: Stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": q}],
    stream=stream,
)
print("A: ", end="")
for chunk in rst:
    chunk: ChatCompletionChunk = chunk
    x = chunk.choices[0].delta.content
    if x:
        print(x, end="", flush=True)