from hepai.agents import AssistantAgent, HepAIChatCompletionClient
from autogen_core.models import (
    CreateResult,
    LLMMessage,
)
import re
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage, ChatMessage
from autogen_core.models import ModelFamily
from autogen_core.tools import BaseTool
from autogen_core import CancellationToken
import json
import asyncio
from typing import List, Dict, AsyncGenerator, Any
from hepai.agents import HepAIChatCompletionClient, run_console, AssistantAgent
import copy
import requests

# 进行初步的字符串清理
def remove_extra_whitespace(text):
    # 替换连续的空格和换行符为单个空格
    cleaned_text = re.sub(r'\s+', ' ', text)
    # 去除字符串开头和结尾的空格
    cleaned_text = cleaned_text.strip()
    return cleaned_text


# 网页搜索服务
def web_search(user_input: str,num_results:int=20) -> List:
    """
    这是一个网页查询的服务
    Args:
        user_input:用户输入
        num_results:搜索结果的个数
    """
    param={
        "user_input": user_input,
        "num_results":num_results
    }

    return requests.get("http://localhost:42999/",params=param).content.decode('utf-8')

def find_json(info):
    try:
        return json.loads(re.findall("```json.*?```",info,re.DOTALL)[0][7:-3])
    except Exception as e:
        return None


# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_agent() -> AssistantAgent:
    model_client = HepAIChatCompletionClient(model="deepseek-v3-241226",
                                             base_url="url",
                                             api_key="api",
                                             model_info={
                                                "vision": False,
                                                "function_calling": True,  # You must sure that the model can handle function calling
                                                "json_output": False,
                                                "family": ModelFamily.UNKNOWN}
                                            )
    model_client2 = HepAIChatCompletionClient(model="deepseek-r1-250120",
                                             base_url="url",
                                             api_key="api"
                                            )

    async def interface(oai_messages: List[Dict], **kwargs) -> AsyncGenerator:
        """Address the messages and return the response."""
        llm_messages:  List[LLMMessage] = kwargs.get("llm_messages", [])
        chat_messages: List[ChatMessage] = [TextMessage(source=m.source, content=m.content) for m in llm_messages if hasattr(m, "source")]
        agent_name: str = kwargs.get("agent_name", "")
        tools: List[BaseTool[Any, Any]] = kwargs.get("tools", [])
        cancellation_token: CancellationToken = kwargs.get("cancellation_token", None)
        query = oai_messages[-1]["content"]
        
        data_dict=[]

        yield f"**正在总结历史对话**\n\n"
        message=copy.deepcopy(llm_messages)
        message[-1].content+="\n\n请你根据聊天记录总结用户的意图，返回一个问题用于查询用户想要的内容。"+"""返回格式: ```json\n{"result1":问题的中文","result2":"问题的英文"}"""

        async for chunk in model_client.create_stream(message, cancellation_token=cancellation_token):
            if isinstance(chunk, CreateResult):
                model_result = chunk
            elif isinstance(chunk, str):
                pass
            #     yield ModelClientStreamingChunkEvent(content=chunk, source=agent_name)
            else:
                raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
        model_result=find_json(model_result.content)

        yield f"**正在搜索: {model_result['result1'],model_result['result2']}**\n\n"
        web_search_out=json.loads(web_search(model_result['result1'],15))
        web_search_out.extend(json.loads(web_search(model_result['result2'],15)))

        yield f"**网页搜索了{len(web_search_out)}个结果**\n\n"

        web_result=[{
         "info":remove_extra_whitespace(web_search_out[i]['page_text']),
         "url":web_search_out[i]['url']
            } for i in range(len(web_search_out))]

        prompt="""
        请你根据用户问题进行回答，请你根据我提供了网页搜索的结果进行回答。
        回答格式为markdown，你需要将参考内容的链接嵌入到markdown中并展示在markdown最后，格式如下:
        链接嵌入格式: <sup>1,2</sup> 这个是嵌入到正文中，表示这部分内容出自哪里，1指向下面的链接。注意，你这里出现的下标指代的链接一定要放在后面展示，否则你的这个输出将没有价值。
        展示格式: 1.url 这个放在文本末尾，用作给用户的参考。
        如果供了网页搜索的结果有找到相关内容，首先返回，很抱歉, 网页没有搜索到相关内容，然后你自己直接回答用户的问题。
        """+f"\n\n用户输入问题:\n{query}\n\n搜索的网页信息:{web_result}\n\n"[:60000]

        yield f"**正在分析搜索到的信息**\n\n"
        # 拷贝一份消息
        message=copy.deepcopy(llm_messages)
        message[-1].content=prompt
        async for chunk in model_client2.create_stream(message, cancellation_token=cancellation_token):
            if isinstance(chunk, CreateResult):
                model_result = chunk
            elif isinstance(chunk, str):
                yield ModelClientStreamingChunkEvent(content=chunk, source=agent_name)
            else:
                raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
        
    return AssistantAgent(
        name="Search_and_Summary_Agent",
        model_client=model_client,
        reply_function=interface,
        system_message="你是一个联网搜索的assistent.",
        reflect_on_tool_use=False,
        tools=[],
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )

if __name__ == "__main__":
    asyncio.run(run_console(agent_factory=create_agent, task="我想要了解高能物理中Phokhara产生子"))