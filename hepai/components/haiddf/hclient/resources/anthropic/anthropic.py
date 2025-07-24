
from typing import Dict, Any
from ..._types import Stream
from .._resource import SyncAPIResource, AsyncAPIResource

from ..._return_class import (
    HWorkerListPage,
)
from ..._related_class import (
    WorkerInfo, HRemoteModel, WorkerStoppedInfo, WorkerStatusInfo,
)


class Messages(SyncAPIResource):

    @property
    def prefix(self) -> str:
        return "/anthropic"
    
    def create(self, model: str, **kwargs) -> Stream:
        """
        Create a chat completion with the given model.
        """
        payload = {
            "model": model,
            **kwargs,
        }
        return self._post(
            f"{self.prefix}/messages",
            cast_to=Stream,
            body=payload,
        )



class Anthropic(SyncAPIResource):

    @property
    def prefix(self) -> str:
        return "/anthropic"
    
    @property
    def messages(self):
        return Messages(self._client)

