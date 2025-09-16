"""
调用Worker的API
"""


import os, sys
from pathlib import Path
import requests
import hai


class HaiLLM(object):

    @staticmethod
    def chat(model, messages=None, **kwargs):
        """Create a LLM instance.

        :param model: The model name.
        :param messages: The messages.
        :return: The LLM instance.
        """
        api_key = kwargs.pop("api_key", None)
        api_key = api_key or hai.api_key

        url = kwargs.pop("url", None)
        if not url:
            # host = kwargs.pop("host", "aiapi.ihep.ac.cn")
            host = kwargs.pop("host", "aiapi.ihep.ac.cn/apiv2")
            port = kwargs.pop("port", None)
            if port is not None:
                url = f"http://{host}:{port}"
            else:
                url = f"https://{host}"
        
        
        data = dict()
        data['model'] = model
        data['messages'] = messages
        data['stream'] = kwargs.pop('stream', True)
        data.update(kwargs)

        assert api_key, """
The HepAI API-KEY is required. Please set the environment variable `HEPAI_API_KEY` via `export HEPAI_API_KEY=xxx`.
Alternatively, it can be provided by passing in the `api_key` parameter when calling the `chat` method.
"""
        session = requests.Session()
        response = session.post(
            f'{url}/v1/chat/completions',
            # f'{url}/v1/inference',
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
            stream=True,
            timeout=60,
            )
        # print(f'llm response: {response}')
        full_response = ""
        # print('llm streaming:')
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if not chunk:
                continue
            chunk = chunk.decode('utf-8')
            if chunk == "[DONE]":
                break
            full_response += chunk
            # print(f'\r{full_response}', end='')
            yield chunk

        # print('\n')
        # print(f'full_response: {full_response}')
        # print(model, messages)


if __name__ == '__main__':
    import sys
    model = 'hepai/chathep-0527'
    model = 'openai/gpt-3.5-turbo'
    api_key = os.getenv('HEPAI_API_KEY')
    messages = [
        {'role': 'system', 'content': 'You are a bot.'},
        {'role': 'user', 'content': 'Hello, how are you?'}
    ]
    # messages = [
    #     {"role": "system", "content": 'Yo'},
    #     {"role": "user", "content": 'Hello'},
    #     ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
    #     ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
    # ]
    result =  HaiLLM.chat(
        model,
        api_key=api_key, 
        messages=messages,
        host="aiapi.ihep.ac.cn", port=42901,
        )
    full_result = ""
    for i in result:
        full_result += i
        sys.stdout.write(i)
        sys.stdout.flush()
    print()
