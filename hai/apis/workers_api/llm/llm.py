

import json
import requests


class HaiLLM(object):

    @staticmethod
    def chat(model, messages=None, **kwargs):
        """Create a LLM instance.

        :param model: The model name.
        :param messages: The messages.
        :return: The LLM instance.
        """

        api_key = kwargs.pop("api_key", None)

        session = requests.Session()
        host = kwargs.get("host", "chat.ihep.ac.cn")
        port = kwargs.get("port", 42901)

        data = dict()
        data['model'] = model
        data['messages'] = messages
        data['stream'] = kwargs.pop('stream', False)
        data.update(kwargs)

        response = session.post(
            f"http://{host}:{port}/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
            stream=True,
            timeout=5,
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
