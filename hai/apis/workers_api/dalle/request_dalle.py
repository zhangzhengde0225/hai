

import os, sys
import hai

def request_model(prompt):

    res = hai.Model.inference(
            model='openai/dalle3',
            prompt=prompt,  # 提示生成图片的文本
            n=1,  # 生成图片的数量
            size=512, # 生成图片的尺寸
            response_format='url',  # 返回的图片格式, url或b64_json
        )
    return res

prompt = 'a white cat'
result = request_model(prompt=prompt)
print(result)



