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