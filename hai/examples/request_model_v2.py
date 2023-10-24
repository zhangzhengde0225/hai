import os, sys
import hai

def request_model(prompt):

    res = hai.Model.inference(
            model='openai/dalle3',
            prompt=prompt,  # 生成图片的文本
            size=1024,
            stream=False,
        )
    # print(res, type(res))
    return res

prompt = 'a white cat'
answer = request_model(prompt=prompt)

