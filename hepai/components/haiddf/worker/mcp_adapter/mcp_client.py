"""
Run from the repository root:
    uv run examples/snippets/clients/streamable_basic.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    # Connect to a streamable HTTP server
    async with streamablehttp_client("http://localhost:42600/apiv2/hepai/custom-model/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            result = await session.call_tool("custom_method", {"a": 5, "b": 7})
            print(f"Result of custom_method(5, 7): {result}")

if __name__ == "__main__":
    asyncio.run(main())