
import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, f"{here.parent.parent}")
    from hepai import __version__

from hepai import HepAI
from hepai.types import ChatCompletion


api_key=os.getenv("DDF_ZDZHANG_API_KEY")
base_url = "https://aiapi001.ihep.ac.cn/apiv2"
client = HepAI(base_url=base_url, api_key=api_key, proxy=None)
q = "Sai hello"

model = "openai/gpt-4o-mini"
# model = "openai/o1-preview"
# 测试非流
print(f"Q: {q}")
rst: ChatCompletion = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": q}],
)
print(f"A: {rst.choices[0].message.content}")