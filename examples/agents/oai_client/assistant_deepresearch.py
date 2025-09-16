from hepai.agents import AssistantAgent, HepAIChatCompletionClient
from autogen_core.models import (
    CreateResult,
    LLMMessage,
)
import re
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage, ChatMessage
from autogen_core.tools import BaseTool
from autogen_core import CancellationToken
import json
import asyncio
from typing import List, Dict, AsyncGenerator, Any
from openai import OpenAI
from autogen_ext.tools.mcp import StdioServerParams,mcp_server_tools
from hepai.agents import HepAIChatCompletionClient, run_console, AssistantAgent
import copy
from concurrent.futures import ThreadPoolExecutor
import requests
from openai import OpenAI

# 进行初步的字符串清理
def remove_extra_whitespace(text):
    # 替换连续的空格和换行符为单个空格
    cleaned_text = re.sub(r'\s+', ' ', text)
    # 去除字符串开头和结尾的空格
    cleaned_text = cleaned_text.strip()
    return cleaned_text

# 提取llm返回结果中的字符串
def find_json(info):
    try:
        return json.loads(re.findall("```json.*?```",info,re.DOTALL)[0][7:-3])
    except Exception as e:
        return None

# 网页搜索服务
def web_search(user_input: str,num_results:int=15) -> List:
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

# 获取大模型输出的结果
async def __get_useful_data__(model_client,llm_messages,cancellation_token):
    async for chunk in model_client.create_stream(
        llm_messages, cancellation_token=cancellation_token
            ):
            if isinstance(chunk, CreateResult):
                model_result = chunk
            elif isinstance(chunk, str):
                yield ModelClientStreamingChunkEvent(content=chunk, source="")
            else:
                raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
    try:
        data= find_json(model_result.content)["result"]
        yield data
    except:
        yield ""
async def get_useful_data(model_client,llm_messages,cancellation_token):
    async for value in __get_useful_data__(model_client,llm_messages,cancellation_token):
        data=value
    return data

# 搜索并网页整理
async def search_and_refine(key,model_client,llm_messages,cancellation_token):
    web_search_out=json.loads(web_search(key))


    # 网页内容初步提取
    # arxiv_search_out=server.arxiv_search(key)
    # prompt=f"对文本信息进行提炼清洗"+"""
    #     返回格式：
    #     ```json{
    #     "result":你提炼的信息，如果没有相关的内容，这里就填空字符串。
    #     }
    #     ```
    # """
    # web_result=[]
    # arxiv_result=[]
    # messages=[copy.deepcopy(llm_messages) for _ in web_search_out]
    # for i in range(len(messages)):
    #     messages[i][-1].content=prompt+web_search_out[i]['page_text']
    # web_result=await asyncio.gather(*[get_useful_data(model_client,i,cancellation_token) for i in messages])

    # messages=[copy.deepcopy(llm_messages) for _ in arxiv_search_out]
    # for i in range(len(messages)):
    #     messages[i][-1].content=prompt+arxiv_search_out[i]['summary']
    # arxiv_result=await asyncio.gather(*[get_useful_data(model_client,i,cancellation_token) for i in messages])
    
    # 这里直接将网页内容初步清洗后放入大模型总结
    web_result=[{
         "info":remove_extra_whitespace(web_search_out[i]['page_text']),
         "url":web_search_out[i]['url']
    } for i in range(len(web_search_out))]

    # arxiv_result=[{
    #      "info":arxiv_result[i],
    #      "url":arxiv_search_out[i]['url']
    # } for i in range(len(arxiv_result))]

    prompt2=f"""
        对输入的内容进行总结提炼,提炼要求如下：
        1.内容需要与{key}相关。
        2.需要尽可能利用给定的文本，需要结合文本进行交叉总结。
        3.用户提供内容的同时会同时提供url链接，你需要在提炼内容是，同时将连接嵌入到markdown中，标签写序号就行。引用链接需要展示在最下面。
        4.最终返回的结果需要尽可能的丰富，包含与{key}相关的的全部内容。
        5.最大返回字数不超过5000字,但也不能过少。

        链接嵌入格式: [xxx](xxxx)
        展示格式: 1.xxxx
        """+"""
        返回格式：
        ```json{
        "result":你提炼的信息，这是一个markdown，如果没有相关的内容，这里就填空字符串。
        }
        ```\n\n
        """

    # resource=f"""网页搜索信息：\n{web_result}\n\n\narxiv搜索信息:\n{arxiv_result}"""
    resource=f"""网页搜索信息：\n{web_result}\n\n\n"""
    messages=copy.deepcopy(llm_messages)
    messages[-1].content=prompt2+resource
    data = await get_useful_data(model_client,messages,cancellation_token)
    return data
    


# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_agent() -> AssistantAgent:
    model_client = HepAIChatCompletionClient(model="deepseek-r1-250120",
                                             base_url="your url",
                                             api_key="your api_key"
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
        # try:
        if True:
            for k in range(4):
                # 设置prompt
                choice_prompt="""
                你是一位智能助手，任务是帮助用户生成问题的简要摘要总结。

                用户会传递问题和检索信息，你需要判断用户传递的信息是否能生成结构充分的摘要总结，摘要总结必须紧扣用户传入的内容，且必须严谨细致，用户传入的信息中包含网页链接，你在写摘要总结的时候需要进行合理引用。引用链接需要展示在最下面。
                
                **任务要求：**
                1. **提取关键信息**：从搜索结果中提取出最重要的信息，包括但不限于主题、核心观点、数据、结论等。
                2. **结构化输出**：将摘要总结分为以下几个部分：
                - **主题**：用一句话概括搜索内容的主题。
                - **核心观点**：列出 2-3 个最核心的观点或发现。
                - **支持数据**：如果有相关数据或事实，请简要列出。
                - **结论**：总结搜索结果的主要结论或建议。
                3. **简洁明了**：语言简洁，避免冗余，每条内容不超过 2 行。
                4. **保持客观**：仅基于搜索结果内容生成摘要，不添加主观推测或额外信息。
                链接嵌入格式: [xxx](xxxx)
                展示格式: 1.xxxx

                如果用户传入的信息足够丰富能生成，则返回相关摘要总结，返回结果如下：
                ```json
                {
                "return":1,
                "info":你生成的摘要总结，markdown格式。
                }
                ```

                如果你认为还可以进一步的检索以返回更完美的结果或者用户没有提供检索信息，则返回如下结果：
                ```json
                {
                "return":0,
                "search_list":[这里面是你觉得需要进一步搜索的关键词,注意 关键字需要为英文,这个关键词会在web上进行检索,列表长度最大为3]
                }

                ```

                用户输入的需要写的摘要总结一段内容:
                -----\n
                    """+chat_messages[-1].content+"\n-----\n\n"
                # llm_messages=chat_messages
                # 拷贝一份消息
                message=[copy.deepcopy(llm_messages[-1])]
                temp_message=choice_prompt+"\n\n".join([f"第{i+1}轮搜索:\n\n"+"\n".join([f"搜索关键字:{j}\n搜索结果:{data_dict[i][j]}\n" for j in data_dict[i]]) for i in range(len(data_dict))])
                message[-1].content=temp_message
                async for chunk in model_client.create_stream(
                            message, cancellation_token=cancellation_token
                        ):
                            if isinstance(chunk, CreateResult):
                                model_result = chunk
                            elif isinstance(chunk, str):
                                yield ModelClientStreamingChunkEvent(content=chunk, source=agent_name)
                            else:
                                raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
                temp_data=find_json(model_result.content)
                if temp_data:
                    if temp_data["return"]:
                        yield f"**输出结果...**\n\n"
                        yield temp_data["info"]
                        break
                else:
                    yield "大模型json解析出错"
                    break
                keys_=temp_data["search_list"]
                with open('key_to_info.json','r',encoding='utf-8') as f:
                   info=json.load(f)
                keys=[]
                key_to_info={}
                for key in keys_:
                    if key in info:
                        key_to_info[key]=info[key]
                    else:
                        keys.append(key)
                yield f"**正在进行第{k+1}层深度搜索，搜索关键字：{keys_}...**\n\n"

                # search_out=[]
                # for key in keys:
                #      search_out.append(await search_and_refine(key,model_client,llm_messages,cancellation_token))
                search_out=await asyncio.gather(*[search_and_refine(key,model_client,llm_messages,cancellation_token) for key in keys])
                search_out={keys[inf]:search_out[inf] for inf in range(len(search_out))}
                yield f"**分析搜索到的文档...**\n\n"
                for key in search_out:
                    if len(key)>200:
                        info[key]=search_out[key]
                    key_to_info[key]=search_out[key]
                with open('key_to_info.json','w',encoding='utf-8') as f:
                    json.dump(info,f,ensure_ascii=False,indent=4)
                data_dict.append(key_to_info)
            else:
                choice_prompt="""
                你是一位智能助手，任务是帮助用户生成问题的简要总结摘要总结。

                用户会传递问题和检索信息，你需要判断用户传递的信息是否能生成结构充分的摘要总结，摘要总结必须紧扣用户传入的内容，且必须严谨细致，用户传入的信息中包含网页链接，你在写摘要总结的时候需要进行合理引用。引用链接需要展示在最下面。
                如果用户传入的信息足够丰富能生成，则返回相关摘要总结，返回结果如下：

                **任务要求：**
                1. **提取关键信息**：从搜索结果中提取出最重要的信息，包括但不限于主题、核心观点、数据、结论等。
                2. **结构化输出**：将摘要总结分为以下几个部分：
                - **主题**：用一句话概括搜索内容的主题。
                - **核心观点**：列出 2-3 个最核心的观点或发现。
                - **支持数据**：如果有相关数据或事实，请简要列出。
                - **结论**：总结搜索结果的主要结论或建议。
                3. **简洁明了**：语言简洁，避免冗余，每条内容不超过 2 行。
                4. **保持客观**：仅基于搜索结果内容生成摘要，不添加主观推测或额外信息。
                链接嵌入格式: ![1](xxxx)
                展示格式: 1.xxxx

                ```json
                {
                "return":1,
                "info":你生成的摘要总结，markdown格式。
                }
                链接嵌入格式: [xxx](xxxx)
                展示格式: 1.xxxx

                用户输入的需要写摘要总结的一段内容:
                -----\n
                            """+chat_messages[-1].content+"\n-----\n\n"
                # llm_messages=chat_messages
                # 拷贝一份消息
                message=[copy.deepcopy(llm_messages[-1])]
                temp_message=choice_prompt+"\n\n".join([f"第{i+1}轮搜索:\n\n"+"\n".join([f"搜索关键字:{j}\n搜索结果:{data_dict[i][j]}\n" for j in data_dict[i]]) for i in range(len(data_dict))])
                message[-1].content=temp_message
                async for chunk in model_client.create_stream(
                            message, cancellation_token=cancellation_token
                        ):
                            if isinstance(chunk, CreateResult):
                                model_result = chunk
                            elif isinstance(chunk, str):
                                yield ModelClientStreamingChunkEvent(content=chunk, source=agent_name)
                            else:
                                raise RuntimeError(f"Invalid chunk type: {type(chunk)}")
                temp_data=find_json(model_result.content)
                if temp_data:
                    if temp_data["return"]:
                        yield f"**输出结果...**\n\n"
                        yield temp_data["info"]
                else:
                    yield "大模型json解析出错"

    return AssistantAgent(
        name="Search_and_Summary_Agent",
        model_client=model_client,
        reply_function=interface,
        system_message="你是一个在查询网页与arxiv并进行总结的工具.",
        reflect_on_tool_use=False,
        tools=[],
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )

if __name__ == "__main__":
    asyncio.run(run_console(agent_factory=create_agent, task="zc(3900)"))