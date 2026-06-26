import json
import boto3
from botocore.config import Config

import os
import dotenv
import sys
from pathlib import Path

here = Path(__file__).parent
dotenv.load_dotenv(here / ".env")  # 优先加载当前目录的 .env 文件，方便不同 worker 定义不同的环境变量

region_name = os.getenv("AWS_REGION", "us-east-1")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
model_id = os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-2")  # 替换为你要使用的 Bedrock 模型 ID


proxy_definitions = {
    'http': 'http://127.0.0.1:8118',
    'https': 'http://127.0.0.1:8118'
}

my_config = Config(
    region_name="us-east-1",
    signature_version='v4',
    proxies=proxy_definitions
)

client = boto3.client(
    "bedrock-runtime",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    config=my_config
)


# body = {
#     "anthropic_version": "bedrock-2023-05-31",
#     "max_tokens": 200,
#     "messages": [
#         {"role": "user", "content": "你好，请用一句话介绍你自己。"}
#     ],
# }

# response = client.invoke_model(
#     modelId=model_id,
#     body=json.dumps(body),
#     contentType="application/json",
#     accept="application/json",
# )

# result = json.loads(response["body"].read())
# print(result["content"][0]["text"])
