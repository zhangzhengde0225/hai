import os
import json
import time
import pytest
import requests
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TestControllerImages():
    api_key = os.environ.get("CONTROLLER_API_KEY")
    base_url = os.environ.get("CONTROLLER_API_BASE_URL")

    def test_openai_controller_responses(self):
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        model_name = "openai/gpt-image-1"
        response = client.images.generate(
            model=model_name,  # 替换为你们实际的模型名
            prompt="一只可爱的赛博朋克风格的小猫，正在敲击机械键盘",
            size="1024x1024",
            quality="low",
            n=1,
        )

        # 打印生成的图片 URL
        image_url = response.data[0].url
        print(f"图片生成成功！URL: {image_url}")
