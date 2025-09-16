import sys
import os

from hepai.agents import AssistantAgent, HepAIChatCompletionClient, DrSaiAPP
from hepai.agents import run_console, run_backend, run_hepai_worker, run_openwebui, run_pipelines,run_drsai_app
from hepai.agents.modules.managers.base_thread import Thread
from hepai.agents.modules.managers.threads_manager import ThreadsManager
import os, json
import asyncio
from typing import List, Dict, Union, AsyncGenerator, Tuple, Any


from autogen_core import CancellationToken
from autogen_core.tools import BaseTool
from autogen_core.models import (
    LLMMessage,
    ChatCompletionClient,
)

# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_agent() -> AssistantAgent:

    async def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"The weather in {city} is 73 degrees and Sunny."
    
    # Define a model client. You can use other model client that implements
    # the `ChatCompletionClient` interface.
    model_client = HepAIChatCompletionClient(
        model="deepseek-r1-250120",
        api_key=os.environ.get("VOLCES_API_KEY"),
        base_url=os.environ.get("VOLCES_BASE_URL"),
        # model="openai/gpt-4o",
        # api_key=os.environ.get("HEPAI_API_KEY"),
    )

    # Address the messages and return the response. Must accept messages and return a string, or a generator of strings.
    async def interface( 
        oai_messages: List[str],  # OAI messages
        agent_name: str,  # Agent name
        llm_messages: List[LLMMessage],  # AutoGen LLM messages
        model_client: ChatCompletionClient,  # AutoGen LLM Model client
        tools: List[BaseTool[Any, Any]],  # AutoGen tools
        cancellation_token: CancellationToken,  # AutoGen cancellation token,
        thread: Thread,  # DrSai thread
        thread_mgr: ThreadsManager,  # DrSai thread manager
        **kwargs) -> Union[str, AsyncGenerator[str, None]]:
        """Address the messages and return the response."""
        yield "test_worker reply"


    # Define an AssistantAgent with the model, tool, system message, and reflection enabled.
    # The system message instructs the agent via natural language.
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        reply_function=interface,
        tools=[get_weather],
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=True,  # Must set to True if reply_function returns a generator.
    )


async def main():

    drsaiapp = DrSaiAPP(agent_factory=create_agent)
    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":"Why will humans be destroyed", "role":"user"}],
        # dialog_id = "22578926-f5e3-48ef-873b-13a8fe7ca3e4",
        )
    model_client_stream = create_agent()._model_client_stream
    async for message in stream:
        oai_json = json.loads(message.split("data: ")[1])
        if model_client_stream:
            textchunck = oai_json["choices"][0]["delta"]["content"]
        else:
            textchunck = oai_json["choices"][0]["message"]["content"]
        if textchunck:
            sys.stdout.write(textchunck)
            sys.stdout.flush()
    print()


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(run_console(agent_factory=create_agent, task="What is the weather in New York?"))
    # asyncio.run(run_backend(agent_factory=create_agent))
    # asyncio.run(run_hepai_worker(agent_factory=create_agent))
    # asyncio.run(run_backend(agent_factory=create_agent, enable_openwebui_pipeline=True))