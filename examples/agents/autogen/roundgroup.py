
from hepai.agents import AssistantAgent, HepAIChatCompletionClient

import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an OpenAI model client.
model_client = HepAIChatCompletionClient(
    model="openai/gpt-4o",
    # api_key="sk-...", # Optional if you have an HEPAI_API_KEY env variable set.
)

# Create the primary agent.
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# Create the critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the primary and critic agents.
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)

# Use `asyncio.run(...)` when running in a script.
# result = await team.run(task="Write a short poem about the fall season.")
# print(result)
# result = asyncio.run(team.run(task="Write a short poem about the fall season."))
# print(result)

# Run the agent and stream the messages to the console.
async def main() -> None:
    await Console(team.run_stream(task="Write a short poem about the fall season."))


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).\
import asyncio
asyncio.run(main())