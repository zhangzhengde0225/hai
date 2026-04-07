import os

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI
import os
import concurrent.futures
from hepai import HepAI
load_dotenv()


class TestControllerResponses():
    api_key = os.environ.get("CONTROLLER_API_KEY")
    base_url = os.environ.get("CONTROLLER_API_BASE_URL")

    def test_anthropic_controller_stream_chat_by_openai_sdk(self):
        from hepai import HepAI

        client = HepAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        model_name = "anthropic/claude-opus-4-5-20251101"
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "hello",
                },
            ],
            stream=True,
        )
        for event in stream:
            print(event)

    def test_anthropic_controller_chat_by_openai_sdk(self):
        from hepai import HepAI

        client = HepAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        model_name = "anthropic/claude-opus-4-5-20251101"
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            stream=False,
        )

        print(response)


    def test_anthropic_controller_chat(self):
        client = Anthropic(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        model_name = "anthropic/claude-opus-4-5-20251101"
        message = client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, Claude",
                }
            ],
            model=model_name,
        )
        print(message.content)

    def test_anthropic_controller_stream_chat(self):
        client = Anthropic(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        model_name = "anthropic/claude-opus-4-5-20251101"

        with client.messages.stream(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, Claude",
                    }
                ],
                model=model_name,
        ) as stream:
            print("Claude 正在思考...\n")

            for chunk in stream.text_stream:
                print(chunk, end="", flush=True)

            print("\n\n--- Stream 结束 ---")


class TestControllerPoolExhaustion():
    api_key = os.environ.get("CONTROLLER_API_KEY")
    base_url = os.environ.get("CONTROLLER_API_BASE_URL")

    def single_request(self, req_id):
        """发送单个请求并捕获异常"""
        client = HepAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        model_name = "anthropic/claude-opus-4-5-20251101"

        try:
            # 发起流式请求，触发服务端的 AttributeError 从而泄露 1 个连接
            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "hello",
                    },
                ],
                stream=True,
            )
            for event in stream:
                pass

        except Exception as e:
            # 打印客户端收到的报错
            print(f"[Req {req_id:03d}] 报错: {type(e).__name__} - {e}")

    def test_reproduce_pool_exhaustion(self):
        """并发发送 150 个请求，打爆连接池"""
        total_requests = 1000
        concurrency = 50  # 50 个线程并发

        print(f"开始发送 {total_requests} 个并发请求...")

        # 使用线程池并发发起请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            # 将 0 到 149 的 ID 传给 single_request 函数
            executor.map(self.single_request, range(total_requests))

        print("测试结束。")