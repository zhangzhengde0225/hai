
from hepai.agents import AssistantAgent, HepAIChatCompletionClient
from autogen_agentchat.ui import Console
import os
import asyncio

# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
model_client = HepAIChatCompletionClient(
    model="openai/gpt-4o",
    # api_key=os.environ.get("HEPAI_API_KEY"),
)


# Define a simple function tool that the agent can use.
# For this example, we use a fake weather tool for demonstration purposes.
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

async def write_code(request: str) -> str:
    """Write code for a given request."""
    return f"{request}."

# Define an AssistantAgent with the model, tool, system message, and reflection enabled.
# The system message instructs the agent via natural language.
agent = AssistantAgent(
    name="weather_agent",
    description="A weather agent that can provide weather information.",
    model_client=model_client,
    tools=[get_weather, write_code],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=False,
    model_client_stream=True,  # Enable streaming tokens from the model client.
)


# # Run the agent and stream the messages to the console.
async def main() -> None:
    await Console(agent.run_stream(task="What is the weather in New York?"))

# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).\

asyncio.run(main())
