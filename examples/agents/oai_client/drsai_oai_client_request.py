from hepai import HepAI 
import os
import json
import requests
import sys

HEPAI_API_KEY = os.getenv("HEPAI_API_KEY")
base_url = "http://localhost:42801/apiv2"
# base_url = "https://aiapi.ihep.ac.cn/apiv2"

client = HepAI(api_key=HEPAI_API_KEY, base_url=base_url)

models = client.models.list()
for idx, model in enumerate(models):
  print(model)

stream = True

completion = client.chat.completions.create(
  model='hepai/drsai',
  messages=[
    # {"role": "user", "content": "请使用百度搜索什么是Ptychography?"}
    {"role": "user", "content": "What is the weather in New York?"}
  ],
  stream=stream,
#   extra_body = {
#     "base_models": "openai/gpt-4o-mini",
#     "base_url": 'https://aiapi.ihep.ac.cn/apiv2'}
)

if stream:
  for chunk in completion:
    if chunk.choices[0].delta.content:
      print(chunk.choices[0].delta.content, end='', flush=True)
  print('\n')

else:
  print(completion)