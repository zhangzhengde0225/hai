import sys
import os


from hepai.agents import AssistantAgent, HepAIChatCompletionClient, DrSaiAPP
from autogen_ext.tools.mcp import StdioServerParams,mcp_server_tools
import os, json
import asyncio

class Tools:
    def __init__(self):
        self.tool_config=[
            {
                "command":"conda",
                "args":[
                    "run",
                    "-n",
                    "hepai",
                    "--live-stream",
                    "python",
                    "examples/agents/oai_client/MCP_tools/mcp_server.py"
                    ],
            }
            
        ]
    # 定义一个名为tool的函数
    async def tool(self):
        tools=[]
        for config in self.tool_config:
            tools.extend(await mcp_server_tools(StdioServerParams(
                                command=config["command"],
                                args=config["args"],
                                env=None)
                        ) )
        return tools


# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
async def create_agent() -> AssistantAgent:

    # Define a model client. You can use other model client that implements
    # the `ChatCompletionClient` interface.
    model_client = HepAIChatCompletionClient(
        model="deepseek-r1-250120",
        api_key=os.environ.get("VOLCES_API_KEY"),
        base_url=os.environ.get("VOLCES_BASE_URL"),
    )


    tools=await Tools().tool()

    # Define an AssistantAgent with the model, tool, system message, and reflection enabled.
    # The system message instructs the agent via natural language.
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=tools,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=False,
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )


async def main():

    drsaiapp = DrSaiAPP(agent_factory=create_agent)
    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":"What is the weather in New York?", "role":"user"}],
        stream=True,)

    async for message in stream:
        oai_json = json.loads(message.split("data: ")[1])
        textchunck = oai_json["choices"][0]["delta"]["content"]
        if textchunck:
            sys.stdout.write(textchunck)
            sys.stdout.flush()
    print()


if __name__ == "__main__":
    asyncio.run(main())
    from hepai.agents import run_console, run_backend, run_hepai_worker, run_openwebui, run_pipelines,run_drsai_app
    # asyncio.run(run_console(agent_factory=create_agent, task="What is the weather in New York?"))
    # asyncio.run(run_backend(agent_factory=create_agent, enable_openwebui_pipeline=True))
    # asyncio.run(run_hepai_worker(agent_factory=create_agent))
    # asyncio.run(run_drsai_app(agent_factory=create_agent,  pipelines_path="your_path_to_drsai/backend/pipelines"))