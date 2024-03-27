
import os, sys
import hepai
hepai.api_key = os.getenv('YSHS_ADMIN_API_KEY')  # 读取环境变量中的 API KEY并设置

# print(hepai.api_key)

def request_model(model, messages, engine=None, **kwargs):
    """统一的请求模型函数"""
    result = hepai.LLM.chat(
            # host="ainpu.ihep.ac.cn",  # 服务器地址
            # port=21601,  # 服务器端口
            url="https://www.yshs.vip",
            api_key=hepai.api_key,  # API KEY
            model=model,  # 模型名称，例如 "openai/gpt-4", 可通过 list_models.py 查看可用模型
            engine=engine,  # 引擎名称, 可选参数，例如 "gpt-4-1106-preview"
            messages=messages,  # 一个会话的消息列表
            stream=True,  # 是否以流式的方式返回结果
            **kwargs  # 其他参数
        )

    full_result = ""
    for i in result:  # result 是一个生成器，每次迭代返回一个消息
        full_result += i
        sys.stdout.write(i)
        sys.stdout.flush()
    print()
    return full_result

def request_gpt35(messages):
    model = "openai/gpt-3.5-turbo"
    return request_model(model, messages=messages)

def request_gpt4(messages):
    model = "openai/gpt-4"
    engine = 'gpt-4-1106-preview'
    # engine = "gpt-4"
    return request_model(model, messages=messages, engine=engine)

if __name__ == '__main__':
    system_prompt = "You are GPT-4, a helpful assistant."  # 系统提示词，指示模型扮演的角色和任务等
    prompt = "hello"  # 提示词，即用户输入的问题
    prompt = "你是GPT-4还是GPT-3.5"
    # prompt = "Are you GPT-4 or GPT-3.5"
    
    # messages代表1个对话，可能有多个轮次，对话有三种角色：system, user, assistant, 分别代表系统、用户、助手
    messages=[
            {"role": "system", "content": system_prompt},  # 设置系统提示词
            {"role": "user", "content": prompt},  # 设置用户输入第1个问题
            ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
            ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
        ]
    # answer = request_gpt35(messages=messages)
    answer = request_gpt4(messages=messages)
