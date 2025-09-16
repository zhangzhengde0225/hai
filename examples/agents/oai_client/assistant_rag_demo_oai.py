import sys
import os



from hepai.agents import AssistantAgent, HepAIChatCompletionClient, DrSaiAPP, run_hepai_worker, run_backend
import os, json
import asyncio
from typing import List, Dict, Union


# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_agent() -> AssistantAgent:

    # Define a model client. You can use other model client that implements
    # the `ChatCompletionClient` interface.
    model_client = HepAIChatCompletionClient(
        model="openai/gpt-4o",
        # api_key=os.environ.get("HEPAI_API_KEY"),
    )


    # Define a simple rag-demo for the assistant.
    async def rag_demo(messages: List[Dict], **kwargs):
        query = messages[-1]["content"]  # Select the last message of the chat history as the RAG query statement.
        retrieve_txt = "1. Humans will be destroyed by AI in 2050;\n2. Humans are destroyed by AI due to their arrogance and conceit."
        last_txt = f"""The following are some reference materials, and you must refer to these materials to answer the question:\n{retrieve_txt}. My question is: {query}"""
        messages[-1]["content"] = last_txt
        return messages



    # Define an AssistantAgent with the model, tool, system message, and reflection enabled.
    # The system message instructs the agent via natural language.
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        memory_function=rag_demo,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )


async def main():

    drsaiapp = DrSaiAPP(agent_factory=create_agent)
    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":"Why will humans be destroyed", "role":"user"}],
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
    from hepai.agents import run_console, run_backend, run_hepai_worker, run_openwebui, run_pipelines,run_drsai_app
    asyncio.run(run_console(agent_factory=create_agent, task="Why will humans be destroyed"))
    # asyncio.run(run_backend(agent_factory=create_agent))
    # asyncio.run(run_hepai_worker(agent_factory=create_agent))
    # asyncio.run(run_backend(agent_factory=create_agent, enable_openwebui_pipeline=True))