from typing import Dict, Any
from ..._types import Stream
from .._resource import SyncAPIResource, AsyncAPIResource
from ..._return_class import HAgentListPage


class Agents(SyncAPIResource):

    @property
    def prefix(self) -> str:
        return "/agents"
    
    def list(self):
        """
        List all agents
        """
        return self._get(
            f"{self.prefix}/list_agents",
            cast_to=HAgentListPage,
        )


class AsyncAgents(AsyncAPIResource):
    """
    Asynchronous version of the Agents resource.
    """

    @property
    def prefix(self) -> str:
        return "/agents"

    async def list_agents(self):
        """
        List all agents asynchronously
        """
        return await self._get(
            f"{self.prefix}/list_agents",
            cast_to=Dict[str, Any],
        )