


import os
import hai

models = hai.Model.list()
print(models)

system_prompt = "You are ChatGPT, answering questions conversationally"
prompt = "Hello!"

api_key = os.getenv('HEPAI_API_KEY')

result = hai.LLM.chat(
        model='hepai/gpt-3.5-turbo',
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
            ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
        ],
        stream=True,
    )

full_result = ""
for i in result:
    full_result += i
    print(f'\r{full_result}', end='')
print()
