from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("HEPAI_API_KEY"),
    base_url="https://aiapi.ihep.ac.cn/apiv2"
)

for model in client.models.list():
    print(model)