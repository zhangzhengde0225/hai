import os, sys
from typing import Dict, Union, Literal, List, Generator, Optional
from pydantic import BaseModel
from dataclasses import dataclass, field
import json
from pathlib import Path
here = Path(__file__).parent
try:
    from hepai import __version__
except:
    sys.path.insert(1, f'{here.parent.parent.parent}')
    from hepai import __version__
import hepai as hai
from hepai import HepAI, AsyncHepAI
from hepai import HRModel, HModelConfig, HWorkerConfig, HWorkerAPP
from hepai.types import ChatCompletion, ChatCompletionChunk
import uvicorn
from fastapi import FastAPI
import threading, time

    

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "function"]
    content: Optional[str | List]
    function_call: Optional[Dict] = None

class ChatCompletionRequest(BaseModel):
    engine: Optional[str] = None
    messages: List[ChatMessage]
    functions: Optional[List[Dict]] = None
    temperature: Optional[float] = None  # between 0 and 2    Defaults to 1
    top_p: Optional[float] = None  # Defaults to 1
    max_length: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None


class WorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(self, config: "ModelConfig"):
        super().__init__(config=config)
        self.cfg = config
        self._client = None
        self.is_o1 = self.judge_is_o1()
        
        if self.cfg.test:
            self.run_test()


    @property
    def client(self):
        if self._client is None:
            if self.cfg.use_async:
                self._client = AsyncHepAI(
                    base_url=self.cfg.base_url,
                    api_key=self.cfg.api_key,
                    proxy=self.cfg.proxy
                )
            else:
                self._client = HepAI(
                    base_url=self.cfg.base_url,
                    api_key=self.cfg.api_key,
                    proxy=self.cfg.proxy
                )
        return self._client

    @property
    def oai_param_keys(self):
#        return [
#            "messages", "model", "frequency_penalty",  "function_call", "functions", "logit_bias", "logprobs", "max_tokens", "n", 
#            "presence_penalty", "response_format", "seed", "stop", "stream", "stream_options", 
#            "temperature", "tool_choice", "tools", "top_logprobs", "top_p", "user", "extra_headers", "extra_query", "extra_body", "timeout"]
        return [
            "messages", "model", "frequency_penalty",  "function_call", "functions", "logit_bias", "logprobs", "max_tokens", "n", 
            "presence_penalty", "response_format", "seed", "stop", "stream", "stream_options", 
            "temperature", "tool_choice", "tools", "top_logprobs", "top_p", "user", "extra_headers", "extra_query", "extra_body", "timeout"]
    
    def judge_is_o1(self):
        if "/" in self.cfg.engine:
            m = self.cfg.engine.split("/")[1]
        else:
            m = self.cfg.engine
        if m in ["o1", "o1-mini", "o1-preview"]:
            return True
        return False

    def response_to_stream(self, response):
        for chunk in response:
            chunk_data = chunk.model_dump()
            if chunk_data["choices"]:
                yield f'data: {json.dumps(chunk_data)}\n\n'

    def request_openai(
            self, 
            oai_messages: List,
#            stream: bool = False,
            extra_headers: None = None,
            **kwargs):
        oai_params = {k: v for k, v in kwargs.items() if k in self.oai_param_keys}
        oai_params.pop("model", None)
        oai_params.pop("messages", None)
#        oai_params.pop("input", None)
        extra_body: Dict = oai_params.pop("extra_body", {})

        print('client.models.list()', self.client.models.list())

#        response = self.client.chat.completions.create(
        response = self.client.embeddings.create(
            model=self.cfg.engine, 
            input=oai_messages, 
#            massages=oai_messages, 
#            stream=stream,
            extra_headers=extra_headers,
            extra_body=extra_body,
            **oai_params
            )
        return response
    

    def run_test(self):

        params = dict()
        q = "Sai hello"
        params['messages'] = [
                {
                "role": "user",
                "content": q,
                }
            ]
        params['stream'] = False
        print(f"Q: {q}")
        print(f"R: ", end="")
        reasoning_flag = False

        response = self.chat_completions(**params)
        for chunk in response:
            chunk: ChatCompletionChunk = chunk
            if isinstance(chunk, str) and chunk.startswith('data: '):
                # chunk = dict(chunk[6::])
                chunk = json.loads(chunk[6::])
                chunk = ChatCompletionChunk(**chunk)
            if reasoning_flag:
                reasoning_content = chunk.choices[0].delta.model_extra.get("reasoning_content", None)
                if reasoning_content:  # 有思考过程
                    print(reasoning_content, end="", flush=True)
                    continue
                if chunk.choices[0].delta.content == "\n\n":
                    # 思考模式结束
                    reasoning_flag = False
                    print(f'A: ', end="")
                    continue

            x = chunk.choices[0].delta.content
            if x:
                print(x, end="", flush=True)
        

    @HRModel.remote_callable
    def chat_completions(self, *args, **kwargs):
        # 请求litellm时需要携带api-key
        if self.cfg.need_external_api_key:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise KeyError("You should provied API-KEY when calling this worker")
            extra_headers = {"Authorization": f"Bearer {api_key}"}
        else:
            extra_headers = kwargs.pop("extra_headers", {})

        request = ChatCompletionRequest(**kwargs)

        #提取request中的message，生成符合openai格式的message
        oai_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages] 
        kwargs = {k: v for k, v in kwargs.items() if k not in ['model', 'messages', 'stream']}

        if self.is_o1:  # o1不允许tempterature、top_p等参数
            kwargs.pop("temperature", None)
            kwargs.pop("top_p", None)

        if request.stream:
            response = self.request_openai(
                oai_messages=oai_messages,
#                stream=True,
                extra_headers=extra_headers,
                **kwargs
            )
            gen: Generator = self.response_to_stream(response)
            return gen
        else:
            response = self.request_openai(
                oai_messages=oai_messages,
#                stream=False,
                extra_headers=extra_headers,
                **kwargs,
            )
            return response

        
@dataclass
class ModelConfig(HModelConfig):
    name: str = field(default="hepai/deepseek-r1:32b", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    
    engine: str = field(default="deepseek-r1:32b", metadata={"help": "Model engine"})
    base_url: str = field(default="<base_url>", metadata={"help": "Base url of the litellm"})
    _api_key: str = field(default=HepAI.NotGiven, metadata={"help": "API key of the model"})
    proxy: str = field(default=None, metadata={"help": "Proxy of the model"})
    need_external_api_key: bool = field(default=False, metadata={"help": "Need external api key from user，就是每次发送请求都需要外部传输过来"})
    use_async: bool = field(default=False, metadata={"help": "whether use async client"})
    test: bool = field(default=True, metadata={"help": "Test model"})

    def __post_init__(self):
        if isinstance(self._api_key, str) and self._api_key.startswith("os.environ/"):
            environ_name = self._api_key.split("/")[1]
            self._api_key = os.getenv(environ_name)
        self.api_key = self._api_key

@dataclass
class WorkerConfig(HWorkerConfig):
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: int = field(default=0, metadata={"help": "Worker's port, default is None, which means auto start from `auto_start_port`"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `auto`"})
    route_prefix: str = field(default="/apiv2", metadata={"help": "Route prefix for worker"})

    controller_address: str = field(default="http://aiapi.ihep.ac.cn:42601", metadata={"help": "Controller's address"})
    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})
    permissions: str = field(default='users: admin; groups: default', metadata={"help": "Model's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    description: str = field(default='This is a demo worker of HEP AI framework (HepAI)', metadata={"help": "Model's description"})
    author: str = field(default=None, metadata={"help": "Model's author"})
    num_workers: int = field(default=1, metadata={"help": "Number of workers"})
    daemon: bool = field(default=True, metadata={"help": "Run as daemon"})
    

    # worker_id: str = field(default=None, metadata={"help": "Worker's id"})

def get_uuid(lenth, prefix=None):
    import uuid
    if prefix:
        return prefix + str(uuid.uuid4())[:lenth-len(prefix)]
    return str(uuid.uuid4())[:lenth]
def start_uvicorn(app, host, port):
    uvicorn.run(app, host=host, port=port)


def run_worker():
    model_config, worker_config = hai.parse_args((ModelConfig, WorkerConfig))
    model = WorkerModel(model_config)  # Instantiate the custom worker model.
    
    if worker_config.num_workers == 1:
        app: FastAPI = HWorkerAPP(model, worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.
        print(app.worker.get_worker_info(), flush=True)
        start_uvicorn(app, app.host, app.port)
    else:
        n = worker_config.num_workers
        threads = []
        for i in range(n):
            w_id = get_uuid(lenth=15, prefix="wk-")
            w_port = worker_config.auto_start_port + i
            app: FastAPI = HWorkerAPP(
                model, worker_config=worker_config, 
                worker_id=w_id, port=w_port)
            print(app.worker.get_worker_info(), flush=True)
            thread = threading.Thread(target=start_uvicorn, args=(app, app.host, app.port))
            thread.start()
            threads.append(thread)
            time.sleep(0.1)
        for t in threads:
            t.join()


if __name__ == "__main__":
    # print(app.worker.get_worker_info(), flush=True)
    run_worker()
    # 启动服务
    # uvicorn.run(app, host=app.host, port=app.port)
    # uvicorn.run("dpsk_worker:app", host=app.host, port=app.port, workers=worker_config.num_workers)
    
