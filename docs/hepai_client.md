

# HepAI Client  

hepai库的客户端HepAI允许用户通用最简单的方式调用HepAI平台的模型，编写符合OpenAI规范，同时支持调用OpenAI的模型。


## 用HepAI客户端调用OpenAI模型

安装hepai库·

```bash
pip install hepai>=1.1.9 --upgrade
```
需要python3.10及以上版本。

一个简单的例子
```python
import os
from typing import Union, Any
from hepai import HepAI, ChatCompletion, Stream, ChatCompletionChunk


client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",
    proxy="<YOUR PROXY URL>",
    )

res: Union[ChatCompletion, Stream, Any] = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! who are you"}
  ],
  stream=True,  # 设置是否流式输出
)

# 返回completion可能是Stream(流式)或ChatCompletion(非流式)或其他类型
if isinstance(res, Stream):
    full_response = ""
    for i, msg in enumerate(res):
        x = msg.choices[0].delta.content if isinstance(msg, ChatCompletionChunk) else msg
        if x:  # x可能为None时略过
            full_response += x
            print(x, end="", flush=True)
    print()
elif isinstance(res, ChatCompletion):
    full_response = res.choices[0].message
    print(full_response)
else:
    print(res)
```


## 用HepAI客户端调用HepAI平台的模型

与OpenAI的调用方式类似，只是base_url, api_key不同，无需使用代理。

```python
import os
api_key=os.getenv("HEPAI_API_KEY")
base_url="https://aiapi.ihep.ac.cn/v1"
proxy=None
```

