from typing import Any, Dict, List
import asyncio
import os, sys



from hepai.agents import AssistantAgent, HandoffTermination, TextMentionTermination
from hepai.agents import HandoffMessage
from hepai.agents import DrSaiSwarm
from hepai.agents import Console, DrSaiAPP
import json
from typing import AsyncGenerator, Union


def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"

# 创建一个工厂函数，用于并发访问时确保后端使用的Agent实例是隔离的。
def create_team() -> DrSaiSwarm:

    travel_agent = AssistantAgent(
        "travel_agent",
        handoffs=["flights_refunder", "user"],
        system_message="""You are a travel agent.
        The flights_refunder is in charge of refunding flights.
        If you need information from the user, you must first send your message, then you can handoff to the user.
        Use TERMINATE when the travel planning is complete.""",
    )

    flights_refunder = AssistantAgent(
        "flights_refunder",
        handoffs=["travel_agent", "user"],
        tools=[refund_flight],
        system_message="""You are an agent specialized in refunding flights.
        You only need flight reference numbers to refund a flight.
        You have the ability to refund a flight using the refund_flight tool.
        If you need information from the user, you must first send your message, then you can handoff to the user.
        When the transaction is complete, handoff to the travel agent to finalize.""",
    )

    termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")

    return DrSaiSwarm([travel_agent, flights_refunder], termination_condition=termination)


async def run_team_stream() -> None:

    task = "I need to refund my flight."

    task_result = await Console(create_team().run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            create_team().run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]

async def handle_oai_stream(stream: AsyncGenerator):
    async for message in stream:
        oai_json = json.loads(message.split("data: ")[1])
        textchunck = oai_json["choices"][0]["delta"]["content"]
        if textchunck:
            sys.stdout.write(textchunck)
            sys.stdout.flush()
    print()

async def main():

    drsaiapp = DrSaiAPP(agent_factory=create_team)
    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":"I need to refund my flight.", "role":"user"}],
        stream=True,
        chat_id = "22578926-f5e3-48ef-873b-13a8fe7ca3e4",
        )
    await handle_oai_stream(stream)

    user_message = input("User: ")

    stream =  drsaiapp.a_start_chat_completions(
        messages=[{"content":user_message, "role":"user"}],
        stream=True,
        chat_id = "22578926-f5e3-48ef-873b-13a8fe7ca3e4",
        )
    await handle_oai_stream(stream)

if __name__ == "__main__":
    asyncio.run(run_team_stream())
    # asyncio.run(main())
