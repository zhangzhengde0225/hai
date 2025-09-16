import asyncio
from autogen_ext.tools.mcp import StdioServerParams,mcp_server_tools,SseServerParams
from drsai import HepAIChatCompletionClient, Console,run_console, AssistantAgent,DrSaiAPP
from autogen_agentchat.base import Response, TaskResult
import os
import json
from mcp.client.sse import sse_client
from autogen_core.models import CreateResult,LLMMessage,UserMessage
import re
import sys
from autogen_agentchat.messages import TextMessage

from autogen_core import CancellationToken
from autogen_core.tools import BaseTool
from autogen_core.models import (
    LLMMessage,
    ChatCompletionClient,
)
from typing import List, Dict, Any, Union, AsyncGenerator
from autogen_agentchat.messages import (
    AgentEvent,
    ChatMessage,
    TextMessage,
    ToolCallSummaryMessage,
    ToolCallRequestEvent,
    ToolCallExecutionEvent,
    ModelClientStreamingChunkEvent,
    MultiModalMessage,
    UserInputRequestedEvent,
)
# 工具类，连接各种mcp工具
class Tools:
    def __init__(self):
        # 本地工具
        self.tool_config=[
            #  {
            #     "command":"conda",
            #     "args":[
            #         "run",
            #         "-n",
            #         "drsai",
            #         "--live-stream",
            #         "python",
            #         "/home/hemf/autoagent/client.py"
            #         ],
            # }   
            {
                "command":"python",
                "args":[
                    "./server.py"
                    ],
            }   
        ]
    # 将所有的工具封装成autogen可使用的工具
    async def tool(self):
        # 创建一个空列表tools，用于存储工具
        tools=[]
        # 遍历self.tool_config中的每一个config
        for config in self.tool_config:
            # 将mcp_server_tools函数返回的值添加到tools列表中
            tools.extend(await mcp_server_tools(StdioServerParams(
                                command=config["command"],
                                args=config["args"],
                                env=None)
                        ))
        return tools
    
    async def get_sse_tool(self,urls):
            tools=[]
            for url in urls:
                tools.extend(await mcp_server_tools(SseServerParams(
                                    url=url,
                                    env=None)
                            ))
            return tools

# 提取llm返回结果中的字符串
def find_json(info):
    try:
        return json.loads(re.findall("```json.*?```",info,re.DOTALL)[0][7:-3])
    except Exception as e:
        return None
    
model_client = HepAIChatCompletionClient(
    model="deepseek-r1-250120",
    base_url="your_api_url",
    api_key="your_api_key")

async def excute_tools_agent(tools) -> AssistantAgent:
   
    return AssistantAgent(
        name="search_and_write",
        model_client=model_client,
        tools=tools,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=True 
    )
    

async def interface(
        oai_messages: List[str],  # OAI messages
        agent_name: str,  # Agent name
        llm_messages: List[LLMMessage],  # AutoGen LLM messages
        model_client: ChatCompletionClient,  # AutoGen LLM Model client
        tools: List[BaseTool[Any, Any]],  # AutoGen tools
        cancellation_token: CancellationToken,  # AutoGen cancellation token,
        **kwargs) -> Union[str, AsyncGenerator[str, None]]:
    
    """Address the messages and return the response."""
        # 定义用户查询语句
    # query=r"给我查询一下 ip 192.168.60.170 port:42998 下 /home/hemf/autoagent/server.py所描绘的程序是什么意思?"
    # query=r"给我查询一下 搜一下 https://www.baidu.com/ 这个网页"
    query = llm_messages[-1].content
    
    # 获取工具
    tools=await Tools().tool()
    
    prompt="将用户输入的内容拆分成多步，返回一个步骤列表， 这个列表里是个字符串，用于作为下一次询问大模型调用function call的输入，记住，这个输入是个promppt,且每一步都会利用到function call的内容，记住，上一步的输出会传递给下一步进行操作，返回格式如下:\n\n"+"""
            ```json
            {
            "result":[步骤，这个步骤是有前后顺序的]
            }
            查询的结果我会自己做单独的处理，因此这里只进行查询的工作。

            用户输入:\n
            """
    transmit_prompt="""
    用户传入的问题:\n{}\n\n
    为了结局这个问题，你正在分步执行任务，分步步骤列表:\n{}\n\n当前正在进行的步骤:\n{}\n\n上一步的输出:\n{}
    """
    last_result=None
    message=[UserMessage(content=prompt+query,source="SystemMessage")]
    # print( "**任务分解中**")

    
    for _ in range(3):
        try:
            yield "**任务分解中**\n\n"
            async for chunk in model_client.create_stream(
                                    message, tools=tools
                                ):
                                    if isinstance(chunk, CreateResult):
                                        model_result = chunk
                                    elif isinstance(chunk, str):
                                        yield  f"{chunk}"
                                    else:
                                        raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
            temp_data=find_json(model_result.content)['result']
            break
        except:
            yield "\n**任务解析失败**\n\n"
    if temp_data:
        for task in temp_data:
            # print( f"**当前正在执行的任务:{task}**")
            yield  f"\n\n**当前正在执行的任务:{task}**\n\n"
            assistant = await excute_tools_agent(tools)
            assistant=assistant.run_stream(task=transmit_prompt.format(query,temp_data,task,last_result))
            async for res in assistant:
                if isinstance(res, TaskResult):
                    try:
                        last_result=json.loads(res.messages[-1].content)
                    except:
                        last_result=res.messages[-1].content
                elif isinstance(res, ModelClientStreamingChunkEvent):
                    yield res.content
                elif isinstance(res, ToolCallRequestEvent):
                    tool_content=res.content
                    for tool in tool_content:
                        yield f'正在执行工具: {tool.name}\n\n'   
            # yield str(last_result)
            try:
                inf=last_result
                if inf["is_sse"]:
                    yield f'**正在连接远程工具**\n\n' 
                    tool_=await Tools().get_sse_tool([f"http://{inf['ip']}:{inf['port']}/sse"])
                    assistant=await excute_tools_agent(tool_)
                    assistant=assistant.run_stream(task=f"{inf['instruction']}\n\n{inf['files']}")
                    async for res in assistant:
                        if isinstance(res, TaskResult):
                            last_result=res.messages[-1].content
                        elif isinstance(res, ModelClientStreamingChunkEvent):
                            yield res.content
                        elif isinstance(res, ToolCallRequestEvent):
                            tool_content=res.content
                            for tool in tool_content:
                                yield f'正在执行工具: {tool.name}\n\n' 
            except:
                pass
        last_prompt="""
        用户传入的问题:\n{}\n\n
        你通过分步运行获得的最终输出:\n{}\n\n
        请你结合运行输出的内容，给用户一个最终答案。
        """
        # print( "**最终总结中**")
        yield "\n\n**最终总结中**\n\n"
        assistant=await excute_tools_agent(tools=[])
        assistant=assistant.run_stream(task=last_prompt.format(query,last_result))
        async for res in assistant:
            if isinstance(res, TaskResult):
                last_result=res.messages[-1].content
            elif isinstance(res, ModelClientStreamingChunkEvent):
                yield res.content
        # print(last_result)
        # yield last_result
    else:
         yield  f"任务执行出错，请重试。"


# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
async def create_agent() -> AssistantAgent:

    # Define a model client. You can use other model client that implements
    # the `ChatCompletionClient` interface.
    model_client = HepAIChatCompletionClient(model="deepseek-r1-250120",
                                              base_url="your base_url",
                                          api_key="your api_key")

    tools=await Tools().tool()
    return AssistantAgent(
        name="search_and_write",
        model_client=model_client,
        # tools=tools,
        reply_function=interface,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=True 
    )



async def main():

    drsaiapp = DrSaiAPP(agent_factory=create_agent)
    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":r"搜一下zc(3900)", "role":"user"}],
        stream=True,)

    async for message in stream:
        oai_json = json.loads(message.split("data: ")[1])
        textchunck = oai_json["choices"][0]["delta"]["content"]
        if textchunck:
            sys.stdout.write(textchunck)
            sys.stdout.flush()
    print()

if __name__ == "__main__":
    # asyncio.run(main())
    from drsai import run_console, run_backend
    asyncio.run(run_backend(
         agent_factory=create_agent, 
         enable_openwebui_pipeline=True,
         port = 42807))
