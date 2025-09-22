from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, APIRouter
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# 创建 FastMCP 实例
mcp = FastMCP(
    name="tools",
    instructions="A collection example of tools for MCP.",
)

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

# 创建 FastAPI 应用
app = FastAPI(title="Integrated API with MCP")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取 MCP 服务器
mcp_server = mcp._mcp_server
sse = SseServerTransport("/mcp/messages/")

# 手动处理 SSE 路由
@app.get("/mcp/sse")
async def handle_mcp_sse(request: Request):
    """Handle MCP SSE connections"""
    async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )

# 处理消息 POST 路由
@app.post("/mcp/messages/")
async def handle_mcp_messages(request: Request):
    """Handle MCP message posts"""
    return await sse.handle_post_message(request.scope, request.receive, request._send)

# 添加其他 API 路由
@app.get("/")
async def root():
    return {
        "message": "Integrated API with MCP",
        "endpoints": {
            "mcp_sse": "/mcp/sse",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "mcp_integrated": True}

@app.get("/api/weather/{city}")
async def api_get_weather(city: str):
    """API endpoint that uses the MCP tool"""
    result = await get_weather(city)
    return {"city": city, "weather": result}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=42996)