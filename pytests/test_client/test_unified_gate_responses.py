import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()


class TestWorkerResponsesByUnifiedGate:
    api_key = os.environ.get("WORKER_API_KEY")
    base_url = os.environ.get("WORKER_API_BASE_URL")

    @pytest.mark.asyncio
    async def test_openai_worker_response_unified(self):
        model_name = "openai/gpt-4.1"
        url = f"{self.base_url}/worker_unified_gate/?model={model_name}&function=responses"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f"{self.api_key}"
        }
        params = {
            'kwargs': {'model': model_name, 'input': 'hello'}
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=headers, json=params, timeout=60)
            print(r.json())

    @pytest.mark.asyncio
    async def test_openai_worker_stream_response_unified(self):
        model_name = "openai/gpt-4.1"
        url = f"{self.base_url}/worker_unified_gate/?model={model_name}&function=responses"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f"{self.api_key}"
        }

        # 1. 在 kwargs 中增加 'stream': True
        params = {
            'kwargs': {
                'model': model_name,
                'input': 'hello',
                'stream': True
            }
        }

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=params, timeout=60) as r:

                if r.status_code != 200:
                    await r.aread()
                    raise Exception(f"Request failed with status {r.status_code}: {r.text}")

                async for line in r.aiter_lines():
                    if line.strip():
                        print(line)

    @pytest.mark.asyncio
    async def test_deepseek_anthropic_messages_unified(self):
        # 1. 配置参数
        model_name = "hepai/deepseek-v4-flash-A2"
        # 确保 base_url 匹配日志中的 http://202.122.37.163:42603/apiv2
        url = f"{self.base_url}/worker_unified_gate/?model={model_name}&function=anthropic_messages"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f"{self.api_key}"
        }

        # 2. 构造符合 Anthropic 格式的 payload
        # 注意：function 为 anthropic_messages 时，kwargs 内部通常期望的是 messages 数组
        params = {
            'kwargs': {
                'model': model_name,
                'messages': [
                    {"role": "user", "content": "你好，请自我介绍一下。"}
                ],
                'max_tokens': 1024,
                'stream': False  # 先测试非流式响应
            }
        }

        # 3. 发起请求
        async with httpx.AsyncClient() as client:
            print(f"\n正在请求 URL: {url}")
            r = await client.post(url, headers=headers, json=params, timeout=60)

            # 4. 调试输出
            print(f"状态码: {r.status_code}")
            try:
                response_json = r.json()
                print("响应内容:", response_json)

                # 如果依然报错，这里会打印出具体的 404 或 400 错误详情
                if r.status_code != 200:
                    pytest.fail(f"请求失败，状态码 {r.status_code}, 详情: {response_json}")

            except Exception as e:
                print(f"无法解析 JSON 响应: {r.text}")
                pytest.fail(f"解析失败: {str(e)}")