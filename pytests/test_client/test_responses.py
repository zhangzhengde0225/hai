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
    async def test_dpsk_chat_completions_httpx(self):
        # 获取环境变量
        api_key = os.environ.get("CONTROLLER_API_KEY")
        base_url = os.environ.get("CONTROLLER_API_BASE_URL")

        if not api_key or not base_url:
            raise ValueError("请确保已设置 CONTROLLER_API_KEY 和 CONTROLLER_API_BASE_URL 环境变量")

        # 拼接完整的请求 URL
        endpoint = f"{base_url.rstrip('/')}/chat/completions"

        # 设置请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 设置请求体参数
        payload = {
            "model": "deepseek-ai/deepseek-v4-pro",
            # "model": "openai/gpt-5.5",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "stream": False
        }

        # 发起异步 HTTP POST 请求
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

            try:
                # 检查 HTTP 状态码是否为 200 OK
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # 💥 发生 HTTP 错误时，打印出完整的请求信息和服务器返回的错误正文
                print(f"\n[{e.response.status_code} Error] 请求失败！")
                print(f"请求 URL: {e.request.url}")
                print(f"请求 Payload: {payload}")
                print(f"服务器返回的错误详情: {e.response.text}")

                # 重新抛出异常，让 pytest 标记该测试失败
                raise

            # 解析并打印 JSON 响应
            result = response.json()
            print(result)

    def test_openai_controller_stream_chat_completions(self):
        import os
        from hepai import HepAI
        client = HepAI(
            api_key=os.environ.get("CONTROLLER_API_KEY"),
            base_url=os.environ.get("CONTROLLER_API_BASE_URL")
        )
        model_name = "openai/gpt-5.5"
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

        model_name = "openai/gpt-5.5"
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

    def test_openai_worker_responses_compact(self):
        """测试 /responses/compact 接口：先创建 response，再 compact。"""
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-5.5"
        # 1. 先创建一个 response
        response = client.responses.create(
            model=model_name,
            input="Hello, this is a test for compact."
        )
        print(f"Created response: {response.id}")

        # 2. 调用 compact
        compacted = client.responses.compact(
            model=model_name,
            previous_response_id=response.id,
        )
        print(f"Compacted response: {compacted.id}")


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

        model_name = "openai/gpt-5.5"
        response = client.responses.create(
            model=model_name,
            input="Hello"
        )

        print(response)

    def test_openai_gpt5_4_pro_controller_responses(self):
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-5.5"
        response = client.responses.create(
            model=model_name,
            input="Hello"
        )

        print(response)

    def test_openai_gpt5_4_pro_2026_03_05_controller_responses(self):
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-5.4-pro-2026-03-05"
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

    def test_openai_controller_responses_compact(self):
        """集成测试：通过 controller 调用 /responses/compact。"""
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-5.5"
        # 1. 先创建一个 response
        response = client.responses.create(
            model=model_name,
            input="Hello, this is a test for compact via controller."
        )
        print(f"Created response: {response.id}")

        # 2. 调用 compact
        compacted = client.responses.compact(
            model=model_name,
            previous_response_id=response.id,
        )
        print(f"Compacted response: {compacted}")


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
            'model': "deepseek-v4-pro",
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

    def test_direct_zhizz_compact(self):
        """测试智增增上游 /v1/responses/compact 接口。"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_secret_key}"
        }
        model_name = "gpt-4.1"

        # 1. 先创建一个 response
        r = httpx.post(
            f"{self.base_url_v1}/responses",
            headers=headers,
            json={'model': model_name, 'input': 'Hello'},
            timeout=30,
        )
        assert r.status_code == 200, f"Create failed: {r.status_code} {r.text[:200]}"
        resp_id = r.json().get('id')
        print(f"Created response: {resp_id}")

        # 2. 调用 compact
        r2 = httpx.post(
            f"{self.base_url_v1}/responses/compact",
            headers=headers,
            json={'model': model_name, 'previous_response_id': resp_id},
            timeout=60,
        )
        print(f"Compact status: {r2.status_code}")
        print(f"Compact body: {r2.text[:500]}")

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
