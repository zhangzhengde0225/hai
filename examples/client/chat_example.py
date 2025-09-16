import os
# 首先设置 API 令牌，使用 pip install hepai -U
from hepai import HepAI

client = HepAI(
    api_key=os.environ.get("HEPAI_API_KEY"),   # 从环境变量中获取 API Key
    base_url="https://aiapi.ihep.ac.cn/apiv2",  # 可选，指定 API 服务器地址
    )

response = client.chat.completions.create(
    # 替换 <MODEL> 为你的Model ID
    model="hepai/deepseek-r1",
    messages=[
        {"role": "user", "content": "Hello"}
    ],
    stream=False,  # 可选，是否使用流式输出
)

print(response)