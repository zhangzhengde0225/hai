from mcp.server.fastmcp import FastMCP

mcp=FastMCP(
    name="tools",
    instructions="A collection example of tools for MCP.",
    # port = 50051, # for transport = "sse" to start a server-sent events (SSE) server
    )

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

if __name__ == "__main__":
    mcp.run(transport="stdio")
