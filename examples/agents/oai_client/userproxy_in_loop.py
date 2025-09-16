import sys
import os

from hepai.agents import HepAIChatCompletionClient
from hepai.agents import AssistantAgent, UserProxyAgent
from hepai.agents import TextMentionTermination
from hepai.agents import RoundRobinGroupChat, DrSaiRoundRobinGroupChat
from hepai.agents import Console
import asyncio

# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_team() -> DrSaiRoundRobinGroupChat:
    # Create the agents.
    model_client = HepAIChatCompletionClient(
        model="deepseek-r1-250120",
        api_key=os.environ.get("VOLCES_API_KEY"),
        base_url=os.environ.get("VOLCES_BASE_URL"),
        # model="openai/gpt-4o",
        # api_key="sk-...", # Optional if you have an HEPAI_API_KEY env variable set.
    )
    assistant = AssistantAgent("assistant", model_client=model_client)
    user_proxy = UserProxyAgent("user_proxy", input_func=input)  # Use input() to get user input from console.

    user_proxy1 = UserProxyAgent("user_proxy1", input_func=input)  # Use input() to get user input from console.

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("APPROVE")

    # Create the team.
    return DrSaiRoundRobinGroupChat([ assistant, user_proxy,], termination_condition=termination)


if __name__ == "__main__":
    from hepai.agents import run_console, run_backend, run_hepai_worker
    asyncio.run(run_console(agent_factory=create_team, task="Write a 4-line poem about the ocean."))
    # asyncio.run(run_backend(agent_factory=create_team))
    # asyncio.run(run_hepai_worker(agent_factory=create_team))
    # asyncio.run(run_backend(agent_factory=create_team, enable_openwebui_pipeline=True))