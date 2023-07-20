


import os, sys
import hai

hai.api_key = os.getenv('HEPAI_API_KEY')

models = hai.Model.list()
print(models)


def request_chatgpt(prompt = "Hello!"):
    system_prompt = "You are ChatGPT, answering questions conversationally"

    result = hai.LLM.chat(
            model='openai/gpt-3.5-turbo',
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
        sys.stdout.write(i)
        sys.stdout.flush()
    print()
    return full_result

answer = request_chatgpt(prompt = "Hello!")
