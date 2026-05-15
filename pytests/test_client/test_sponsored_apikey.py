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
            api_key=os.environ.get("CONTROLLER_SPONSOR_API_KEY"),
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