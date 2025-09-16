

import os, sys
import base64
from pathlib import Path
here = Path(__file__).parent
from hepai import HepAI

api_key = os.getenv("HEPAI_API_KEY")
base_url = "https://aiapi.ihep.ac.cn/apiv2"
client = HepAI(api_key=api_key, base_url=base_url) # set proxy to base_url

q = "给我一张图片，内容是：一只猫在草地上玩耍"
model = "openai/gpt-image-1"

print(f'使用模型`{model}`生成图像`{q}`，生成中...')
img = client.images.generate(
    model=model,
    prompt=q,
    n=1,
    size="1024x1024"
)

image_bytes = base64.b64decode(img.data[0].b64_json)
with open(f"{here}/output.png", "wb") as f:
    f.write(image_bytes)

print(f"Q: {q}, image saved to {here}/output.png")
