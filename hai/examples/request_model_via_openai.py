
import os, sys
from pathlib import Path
here = Path(__file__).parent
try:
    from hepai import HepAI
except:
    sys.path.insert(0, f'{here.parent.parent}')
    from hepai import HepAI
    # from hepai import ChatCompletion

client = HepAI(
    api_key=os.getenv("YSHS_ADMIN_API_KEY"),
    base_url="http://ainpu.ihep.ac.cn:21601/v1",
)
 
models = client.list_models()
print(models)


# 把文件内容放进请求中
messages=[
    {
        "role": "system",
        "content": "你是一个HepAI助手",
    },
    {"role": "user", "content": "你好"},
]
 
stream = False
res = client.chat.completions.create(
#   model="moonshot-v1-32k",
#   model='gpt-4-turbo-preview',
    # model='openai/gpt-3.5-turbo',
    model = "hepai/demo_worker",
  messages=messages,
  temperature=0.3,
  stream=stream,
)

if not stream:
    if res.choices:
        print(res.choices[0].message)
    else:
        print(res.model_extra)
else:
    full_answer = ''
    for chunk in res:
        if chunk.choices:
            choices_list = []
            answer = chunk.choices[0].delta.content
            if answer:
                print(f'{answer}', end='', flush=True)
                full_answer += answer
    print()