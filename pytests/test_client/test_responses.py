from dotenv import load_dotenv

load_dotenv()


def test_dpsk_chat_completion():
    import os
    # 首先设置 API 令牌，使用 pip install hepai -U
    from hepai import HepAI

    client = HepAI(
        api_key=os.environ.get("HEPAI_API_KEY"),  # 从环境变量中获取 API Key
        base_url=os.environ.get("HEPAI_API_BASE_URL")
    )

    model_name = "deepseek-ai/deepseek-r1"
    response = client.chat.completions.create(
        # 替换 <MODEL> 为你的Model ID
        model=model_name,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        stream=False,  # 可选，是否使用流式输出
    )

    print(response)


def test_dpsk_worker_chat_completion():
    import os
    # 首先设置 API 令牌，使用 pip install hepai -U
    from hepai import HepAI

    client = HepAI(
        api_key=os.environ.get("WORKER_API_KEY"),  # 从环境变量中获取 API Key
        base_url=os.environ.get("WORKER_API_BASE_URL")
    )

    model_name = "deepseek-ai/deepseek-r1"
    response = client.chat.completions.create(
        # 替换 <MODEL> 为你的Model ID
        model=model_name,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        stream=False,  # 可选，是否使用流式输出
    )

    print(response)

def test_gpt_worker_chat_completion():
    import os
    # 首先设置 API 令牌，使用 pip install hepai -U
    from hepai import HepAI

    client = HepAI(
        api_key=os.environ.get("WORKER_API_KEY"),  # 从环境变量中获取 API Key
        base_url=os.environ.get("WORKER_API_BASE_URL")
    )

    model_name = "openai/gpt-4.1"
    response = client.chat.completions.create(
        # 替换 <MODEL> 为你的Model ID
        model=model_name,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        stream=False,  # 可选，是否使用流式输出
    )

    print(response)

def test_gpt_worker_responses():
    import os
    # 首先设置 API 令牌，使用 pip install hepai -U
    from hepai import HepAI

    client = HepAI(
        api_key=os.environ.get("WORKER_API_KEY"),  # 从环境变量中获取 API Key
        base_url=os.environ.get("WORKER_API_BASE_URL")
    )

    model_name = "openai/gpt-4.1"
    response = client.responses.create(
        model=model_name,
        input="Hello"
    )

    print(response.output_text)

def test_openai_gpt_worker_responses():
    import os
    from openai import OpenAI

    # 在初始化客户端时传入自定义的 key 和 url
    client = OpenAI(
        api_key=os.environ.get("WORKER_API_KEY"),
        base_url=os.environ.get("WORKER_API_BASE_URL")
    )

    model_name = "openai/gpt-4.1"
    response = client.responses.create(
        model=model_name,
        input="Hello"
    )

    print(response.output_text)
