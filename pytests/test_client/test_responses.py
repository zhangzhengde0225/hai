import os
import json
import time
import pytest
import requests
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TestChatCompletions():
    def test_dpsk_chat_completions(self):
        import os
        from hepai import HepAI

        client = HepAI(
            api_key=os.environ.get("CONTROLLER_API_KEY"),
            base_url=os.environ.get("CONTROLLER_API_BASE_URL")
        )

        model_name = "deepseek-ai/deepseek-r1"
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            stream=False,
        )

        print(response)

    def test_openai_controller_stream_chat_completions(self):
        import os
        from hepai import HepAI
        client = HepAI(
            api_key=os.environ.get("CONTROLLER_API_KEY"),
            base_url=os.environ.get("CONTROLLER_API_BASE_URL")
        )
        model_name = "openai/gpt-4.1"
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'double bubble bath' five times fast.",
                },
            ],
            stream=True,
        )
        for event in stream:
            print(event)

    def test_dpsk_worker_chat_completion(self):
        import os
        from hepai import HepAI

        client = HepAI(
            api_key=os.environ.get("WORKER_API_KEY"),
            base_url=os.environ.get("WORKER_API_BASE_URL")
        )

        model_name = "deepseek-ai/deepseek-r1"
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            stream=False,
        )

        print(response)

    def test_gpt_worker_chat_completion(self):
        import os
        from hepai import HepAI

        client = HepAI(
            api_key=os.environ.get("WORKER_API_KEY"),
            base_url=os.environ.get("WORKER_API_BASE_URL")
        )

        model_name = "openai/gpt-4.1"
        response = client.chat.completions.create(
            # 替换 <MODEL> 为你的Model ID
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            stream=False,
        )

        print(response)


class TestWorkerResponses():
    api_key = os.environ.get("WORKER_API_KEY")
    base_url = os.environ.get("WORKER_API_BASE_URL")

    def test_openai_worker_responses(self):
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-4.1"
        response = client.responses.create(
            model=model_name,
            input="Hello"
        )

        print(response.output_text)

    def test_openai_worker_stream_responses(self):
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        model_name = "openai/gpt-4.1"
        stream = client.responses.create(
            model=model_name,
            input='hello',
            stream=True,
        )
        for event in stream:
            print(event)


class TestControllerResponses():
    api_key = os.environ.get("CONTROLLER_API_KEY")
    base_url = os.environ.get("CONTROLLER_API_BASE_URL")

    def test_openai_controller_responses(self):
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-4.1"
        response = client.responses.create(
            model=model_name,
            input="Hello"
        )

        print(response)

    def test_openai_controller_stream_responses(self):
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        model_name = "openai/gpt-4.1"
        stream = client.responses.create(
            model=model_name,
            input='hello',
            stream=True,
        )
        for event in stream:
            print(event)


class TestZhizzAPI:
    api_secret_key = os.environ.get("ZHIZENGZENG_API_KEY")
    base_url_v1 = "https://api.zhizengzeng.com/v1"

    def test_direct_zhizz(self):
        url = f"{self.base_url_v1}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self.api_secret_key}"
        }
        params = {
            'user': '张三',
            'model': "gpt-3.5-turbo",
            'messages': [{'role': 'user', 'content': '1+100='}]
        }
        r = requests.post(url, json.dumps(params), headers=headers)
        print(r.json())

    @pytest.mark.asyncio
    async def test_direct_response_zhizz2(self):
        url = f"{self.base_url_v1}/responses"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self.api_secret_key}"
        }
        # 这里不能写成 openai/gpt-4.1, 否则会报错
        model_name = "gpt-4.1"
        params = {'model': model_name, 'input': 'hello'}

        async with httpx.AsyncClient() as client:
            # 注意这里保留了你之前改好的 timeout=60
            r = await client.post(url, headers=headers, json=params, timeout=60)
            print(r.json())

    def test_openai_zhizz_responses(self):
        client = OpenAI(
            api_key=self.api_secret_key,
            base_url=self.base_url_v1
        )
        model_name = "gpt-4.1"
        response = client.responses.create(
            model=model_name,
            input="Hello"
        )
        print(response.output_text)

    def test_openai_zhizz_stream_responses(self):
        client = OpenAI(
            api_key=self.api_secret_key,
            base_url=self.base_url_v1
        )
        model_name = "gpt-4.1"
        stream = client.responses.create(
            model=model_name,
            input=[
                {
                    "role": "user",
                    "content": "Say 'double bubble bath' five times fast.",
                },
            ],
            stream=True,
        )
        for event in stream:
            print(event)
