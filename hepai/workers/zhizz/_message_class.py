from typing import Generator, Union, Dict, List, Optional, Literal, Iterator, Any, Iterable
from pydantic import BaseModel
# from ._related_class import OpenAIError
from hepai import HepAI

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "function"]
    content: Optional[str | List]
    function_call: Optional[Dict] = None


class ChatCompletionRequest(BaseModel):
    engine: Optional[str] = None
    messages: List[ChatMessage]
    functions: Optional[List[Dict]] = None
    temperature: Optional[float] = None  # between 0 and 2    Defaults to 1
    top_p: Optional[float] = None  # Defaults to 1
    max_length: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None


# class UDFApiError(OpenAIError):
#     def __init__(self, message, status: int = 500, code="server_error"):
#         super(UDFApiError, self).__init__(message)
#         self.http_status = status
#         self._message = message
        
class EmbeddingsRequest(BaseModel):
    input: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]]
    model: str
    dimensions: int = HepAI.NotGiven
    encoding_format: Literal["float", "base64"] = HepAI.NotGiven
    user: str = HepAI.NotGiven

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: str = "dall-e-2"
    background: Optional[Literal["transparent", "opaque", "auto"]] = HepAI.NotGiven
    moderation: Optional[Literal["low", "auto"]] = HepAI.NotGiven
    n: Optional[int] = 1
    output_compression: Optional[int] = HepAI.NotGiven
    output_format: Optional[Literal["png", "jpeg", "webp"]] = HepAI.NotGiven
    partial_images: Optional[int] = HepAI.NotGiven
    quality: Optional[Literal["auto", "high", "medium", "low", "hd", "standard"]] = HepAI.NotGiven
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    size: Optional[str] = HepAI.NotGiven
    stream: Optional[bool] = HepAI.NotGiven
    style: Optional[Literal["vivid", "natural"]] = HepAI.NotGiven
    user: Optional[str] = HepAI.NotGiven

