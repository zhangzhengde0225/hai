
import httpx
# from .openai_api.adapted_openai._exceptions import APIStatusError
from .openai_api import APIStatusError




class HAPIStatusError(APIStatusError):
    response: httpx.Response
    status_code: int
    request_id: str | None

    def __init__(self, message: str, *, response: httpx.Response, body: object | None) -> None:
        super().__init__(message, response=response, body=body)
        
    def __repr__(self):
        return f'{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code!r}, request_id={self.request_id!r})'

    def __str__(self):
        # 只显示类名和消息
        return f'{self.__class__.__name__}: {self.args[0]}'

