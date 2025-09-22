"""
Deprecated
"""

from typing import List, Callable, Dict
from dataclasses import field, dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi import FastAPI

from .._worker_class import CommonWorker
from ..utils import(
    read_request_body
    )
from ..worker_app import HWorkerAPP, FunctionParamsItem
from ..singletons import authorizer

api_key_auth: Callable = Depends(authorizer.api_key_auth)


@dataclass
class MCPRouterGroup:
    name: str = "mcp"
    prefix: str = "/apiv2"
    tags: List[str] = field(default_factory=lambda: ["mcp"])
    router: APIRouter = field(default_factory=APIRouter)
    parent_app: HWorkerAPP = None  # type: ignore

    def __post_init__(self):
        
        self.count = 0
        rt = self.router
        
        from mcp.server.sse import SseServerTransport
        from mcp.server import Server
        
        self.sse: SseServerTransport = SseServerTransport("/mcp/messages/")
        self._mcp_server: Server = None  # type: ignore

        rt.get("/mcp/sse", dependencies=[api_key_auth])(self.handle_mcp_sse)
        rt.post("/mcp/messages", dependencies=[api_key_auth])(self.handle_mcp_messages)

    @property
    def mcp_server(self):
        if self._mcp_server is None:
            if self.parent_app is None:
                raise ValueError("parent_app is not set.")
            worker = self.parent_app.worker
            mcp = self.construct_mcp_for_worker(worker)
            self._mcp_server = mcp._mcp_server  # type: ignore
        return self._mcp_server

    async def handle_mcp_sse(self, request: Request):
        """Handle MCP SSE connections"""
        async with self.sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            return await self.mcp_server.run(
                read_stream,
                write_stream,
                self.mcp_server.create_initialization_options(),
            )

    async def handle_mcp_messages(self, request: Request):
        """Handle MCP message posts"""
        return await self.sse.handle_post_message(request.scope, request.receive, request._send)
    
    
    def construct_mcp_for_worker(self, worker: CommonWorker):
        from mcp.server.fastmcp import FastMCP
        from mcp.server.sse import SseServerTransport
        mcp = FastMCP(
            name="tools",
            instructions="A collection example of tools for MCP.",
        )
        
        
        return worker
