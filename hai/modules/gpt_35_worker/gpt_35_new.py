# (1) 实现WorkerModel
import os, sys
from pathlib import Path
import json
from dataclasses import dataclass, field
import requests
import damei as dm
logger = dm.get_logger('gpt_35.py')

here = Path(__file__).resolve().parent

# try:
#     from HaiServ.workers.gpt_35.token_usage import TokenUages
# except:
#     sys.path.append(str(here.parent.parent.parent))
#     from HaiServ.workers.gpt_35.token_usage import TokenUages
try:
    import hai
    from hai import BaseWorkerModel
except:
    sys.path.append(str(here.parent.parent.parent))
    import hai
    from hai import BaseWorkerModel

@dataclass
class ModelArgs:
    name: str = "openai/gpt-3.5-turbo"  # 模型名
    proxy: str = None  # 代理
    engine: str = "gpt-3.5-turbo"  # 引擎
    temperature: float = 0.5  # 温度


class WorkerModel(BaseWorkerModel):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        assert self.name is not None, "name must be specified"
        self.session = requests.Session()
        self.proxy = kwargs.get("proxy", None)
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}
        else:
            self.session.proxies = None
        self.api_key = kwargs.get("api_key", os.environ.get('OPENAI_API_KEY', None))
        self.engine = kwargs.get("engine", None)
        assert self.engine is not None, "Engine must be specified, please set it via --engine"
        self.temperature = kwargs.get("temperature", 0.5)
        self.top_p = kwargs.get("top_p", 1.0)
        self.reply_count = kwargs.get("reply_count", 1)

        # self.token_usage = TokenUages()


    @BaseWorkerModel.auto_stream  # 自动将各种类型的输出转为流式输
    def inference(self, **kwargs):
        # 自己的执行逻辑, 例如: # 
        logger.info(f'kwargs: {kwargs}')
        stream = kwargs.get("stream", True)
        messages = kwargs.get("messages", None)
        api_key = kwargs.get("api_key", self.api_key)
        assert api_key is not None, "The api_key must be specified, or set the OPENAI_API_KEY environment variable."

        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            proxies=self.session.proxies,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": self.engine,
                "messages": messages,
                "stream": stream,
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "n": kwargs.get("n", self.reply_count),
                # "user": role,
                # "max_tokens": self.get_max_tokens(convo_id=convo_id),
            },
            stream=stream,
        )

        # print(f'response: {response}')

        if response.status_code != 200:
            raise KeyError(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        
        response_role: str = None
        full_response: str = ""
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue
            if "role" in delta:
                response_role = delta["role"]
            if "content" in delta:
                content = delta["content"]
                full_response += content
                # print(f'\r{full_response}', end='')
                yield content
        # 来保存用量信息
        user_name = kwargs.get('user_name', None)
        # self.token_usage(user_name, messages, full_response, model_name=self.name)

# (2) worker的参数配置和启动代码


# 用dataclasses修饰器快速定义参数类
@dataclass
class WorkerArgs:
    host: str = "0.0.0.0"  # worker的地址，0.0.0.0表示外部可访问，127.0.0.1表示只有本机可访问
    port: str = "auto"  # 默认从42902开始
    controller_address: str = "http://aiapi.ihep.ac.cn:42901"  # 控制器的地址
    worker_address: str = "auto"  # 默认是http://<ip>:<port>
    limit_model_concurrency: int = 5  # 限制模型的并发请求
    stream_interval: float = 0.  # 额外的流式响应间隔
    no_register: bool = False  # 不注册到控制器
    permissions: str = 'groups: all'  # 模型的权限授予，分为用户和组，用;分隔
    description: str = None  # 模型的描述
    author: str = None  # 模型的作者
    test: bool = False  # 测试模式，不会真正启动worker，只会打印参数


def test(model):
    # system_prompt = 'You are GPT-4, answering questions conversationally.'
    system_prompt = ''
    prompt = '你是GPT-3.5还是GPT-4？'
    
    messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
            ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
        ]

    res = model.inference(messages=messages, stream=True)
    print(f'Q: {prompt}')
    print(f'A: ', end='')
    full_result = ""
    for i in res:
        full_result += i
        sys.stdout.write(i)
        sys.stdout.flush()
    print()


# 启动worker的函数
def run_worker(**kwargs):
    # worker_args = hai.parse_args_into_dataclasses(WorkerArgs)  # 解析参数
    model_args, worker_args = hai.parse_args_into_dataclasses((ModelArgs, WorkerArgs))  # 解析多个参数类

    logger.info(model_args)
    logger.info(worker_args)


    model = WorkerModel(  # 获取模型
        **model_args.__dict__,
    )

    if worker_args.test:
        test(model)

    hai.worker.start(
        daemon=False,  # 是否以守护进程的方式启动
        model=model,
        worker_args=worker_args,
        **kwargs
        )
    
if __name__ == '__main__':
    run_worker()
