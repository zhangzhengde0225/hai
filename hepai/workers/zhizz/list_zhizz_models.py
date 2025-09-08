


import os, sys
from pathlib import Path
from hepai import HepAI
from dotenv import load_dotenv
here = Path(__file__).parent

load_dotenv(f'{here.parent.parent.parent}/.env')

api_key = os.getenv("ZHIZENGZENG_API_KEY")
base_url = "https://api.zhizengzeng.com/v1"

api_key = "sk-lZvDMeNaRjKjGtrLArHsVOFtfCLbJuuHWxrBuTIREHsjDqT"
base_url = "http://localhost:42602/apiv2"
model = "openai/gpt-4o"
model = "deepseek-ai/deepseek-v3"

print(f"api_key: {api_key}")
client = HepAI(api_key=api_key, base_url=base_url) # set proxy to base_url

models = client.models.list()
for m in models:
    print(f'  {m}')
print(f"total models: {len(models.data)}")


from hepai import HepAI, Stream, ChatCompletionChunk, ChatCompletion

q = "tell me story"
q = "hello"
stream = True

response: Stream = client.chat.completions.create(
    model=model,
    messages = [
        {
        "role": "user",
        "content": q,
        }
    ],
    stream=stream,
    # extra_body={"user": "test_customer"}
    )

print(f"Q: {q}")

if stream:
    print(f"R: ", end="")
    reasoning_flag = True
    for chunk in response:
        chunk: ChatCompletionChunk = chunk
        
        if chunk is None:
            continue

        if reasoning_flag:
            if not chunk.choices:
                continue
            reasoning_content = chunk.choices[0].delta.model_extra.get("reasoning_content", None)
            if reasoning_content:  # 有思考过程
                print(reasoning_content, end="", flush=True)
                continue
            if chunk.choices[0].delta.content == "\n\n":
                # 思考模式结束
                reasoning_flag = False
                print(f'A: ', end="")
                continue

        x = chunk.choices[0].delta.content
        if x:
            print(x, end="", flush=True)
        
        # print(chunk)
             
else:
    x: ChatCompletion = response
    # print(x.choices[0].message.content)

    print(x)

print()

