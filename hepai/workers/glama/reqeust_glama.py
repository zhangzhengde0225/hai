import os
from openai import OpenAI

api_key = os.getenv("GLAMA_API_KEY")
print(f"Using GLAMA_API_KEY: {api_key}")
client = OpenAI(
    api_key=api_key,
    base_url="https://glama.ai/api/gateway/openai/v1",
)

models = client.models.list()
for model in models:
    if "google" in model.id:
        print(f'  {model.id}')


model="claude-opus-4-5-20251101"
completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    # extra_body={"enable_thinking": False},
)
# print(completion.model_dump_json())
print(completion.choices[0].message.content)