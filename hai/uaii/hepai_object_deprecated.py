
from typing import (
    Mapping, Union, Literal, Iterable, Optional, Dict, List, cast, Type,
    Any,
)
import httpx
import os, sys
from pathlib import Path
here = Path(__file__).parent

import inspect

## opneai
from openai import OpenAI, resources
from openai import NOT_GIVEN, Timeout, NotGiven
from openai._types import Headers, Query, Body
from openai.types import Completion, ChatModel
from openai.resources import Chat

# from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

# adopt to openai v1.63.2
from openai.resources.chat.completions.completions import (
    ChatCompletionMessageParam,
    completion_create_params,
    ChatCompletionToolChoiceOptionParam,
    # ChatCompletionToolParam,
    # ChatCompletionToolUnionParam,
    ChatCompletion,
    ChatCompletionChunk,
    Stream,
    Completions,
    ChatCompletionStreamOptionsParam,
)

from openai._utils import required_args, maybe_transform
from openai._base_client import (
    ResponseT, APIResponse, FinalRequestOptions, RAW_RESPONSE_HEADER, _T,
    Stream, SSEDecoder, AsyncStream, SSEBytesDecoder,
    make_request_options, LegacyAPIResponse, BaseAPIResponse,
    get_origin, extract_response_type
)

from hai.apis.workers_api.model import HaiModel
from .utils.general import load_image_from_bytes
from .utils.file_object import HaiFile

DEFAULT_MAX_RETRIES = 2
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

class HaiPostParser:
    def __call__(self, parsed, **kwargs):
        if isinstance(parsed, ChatCompletion):
            """服务端仅仅返回字典时"""
            if parsed.id is None and parsed.choices is None:
                if parsed.model_extra:
                    return parsed.model_extra

        return parsed

class HAPIResponse(APIResponse):

    def get_filename(self, response: httpx.Response) -> str:
        content_disposition = response.headers.get("content-disposition", "")
        filename = content_disposition.split("filename=")[-1]
        return filename.strip('"')
     
    def _parse(self, *, to: type[_T] | None = None) -> Any | _T:
        response = self.http_response
        content_type, *_ = response.headers.get("content-type", "*").split(";")
        if "image/" in content_type:
            filename = self.get_filename(response)
            return HaiFile(type_="image", data=response.content, filename=filename)
        elif "application/pdf" in content_type:
            filename = self.get_filename(response)
            return HaiFile(type_="pdf", data=response.content, filename=filename)
        elif ("text/" in content_type) and ("event-stream" not in content_type):
            # Fix text/event-stream parse error in 202404
            filename = self.get_filename(response)
            return HaiFile(type_="txt", data=response.content, filename=filename)
        # application/json时
        return super()._parse(to=to)


class HaiCompletion(ChatCompletion):
    pass

class HaiCompletions(Completions):

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        # tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        # tools: Iterable[ChatCompletionToolUnionParam] | NotGiven = NOT_GIVEN,
        tools: None | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "functions": functions,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "stream_options": stream_options,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParams,
            )
        options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            )
        res = self._post(
            "/chat/completions", 
            body=body, options=options,
            cast_to=ChatCompletion,
            stream=stream or False,
            stream_cls=Stream[ChatCompletionChunk],
        )

        return res


    def request_worker(
            self,
            *,
            model: str,
            function: str,
            stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
            extra_headers: Headers | None = None,
            extra_query: Query | None = None,
            extra_body: Body | None = None,
            timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
            **kwargs,
        ):
        tmp = dict()
        tmp["model"] = model
        tmp["function"] = function
        tmp.update(kwargs)
        body=maybe_transform(tmp, completion_create_params.CompletionCreateParams)
        options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            )
        options["post_parser"] = HaiPostParser()
        res = self._post(
            "/worker/unified_gate", 
            body=body, 
            options=options,
            cast_to=HaiCompletion,
            stream=stream or False,
            stream_cls=Stream[ChatCompletionChunk],
        )
        return res

    def verify_api_key(
            self, 
            api_key: str, 
            extra_headers: Headers | None = None,
            extra_query: Query | None = None,
            extra_body: Body | None = None,
            timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
            **kwargs):
        
        params = {
            "api_key": api_key,
        }
        params.update(kwargs)
        options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            )
        try:
            res = self._post(
                "/verify_api_key", 
                body=params, 
                options=options,
                cast_to=HaiCompletion,
                stream=False,
            )
            rst = res.model_extra
        except Exception as e:
            status_code = getattr(e, "status_code", None)
            if status_code == 401:  # 验证失败
            # if status_code.status_code == 401:  # 验证失败
                response = getattr(e, "response", None)
                detail = response.json().get("detail", "")
                rst = {"success": False, "detail": detail}
            else:
                raise e
        return rst



class HaiChat(Chat):
    @property
    def completions(self) -> HaiCompletions:
        return HaiCompletions(client=self._client)

class HepAI(OpenAI):
    completions: HaiCompletions
    chat: HaiChat

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,

        _strict_response_validation: bool = False,
        proxy: str | None = None,
    ) -> None:
        if (http_client is None) and (proxy is not None):
            http_client = self.get_http_client(proxy, base_url=base_url, timeout=timeout,)

        super().__init__(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )
        
        self.completions = HaiCompletions(client=self)
        self.chat = HaiChat(client=self)

        ## 2024.11.13 更新支持DDF Client
        from hepai.modules.haiddf.client.haiddf_client import HaiDDFClient
        timeout = None if (timeout == NOT_GIVEN or timeout is None) else timeout
        self.ddf = HaiDDFClient(api_key=api_key, base_url=base_url, timeout=timeout, proxy=proxy)
    
    @classmethod
    def get_http_client(cls, proxy, **kwargs) -> httpx.Client:
        if proxy is None:
            return None
        else:
            proxies = {
                "http://": proxy,
                "https://": proxy,
            }
        base_url = kwargs.get("base_url", None)
        base_url = base_url or "https://aiapi.ihep.ac.cn/v1"
        timeout = kwargs.get("timeout", DEFAULT_TIMEOUT)
        timeout = DEFAULT_TIMEOUT if (timeout == NOT_GIVEN or timeout is None) else timeout
        transport = kwargs.get("transport", None)
        limits = kwargs.get("limits", DEFAULT_LIMITS)
        limits = DEFAULT_LIMITS if (limits == NOT_GIVEN or limits is None) else limits
        http_client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            proxies=proxies,
            transport=transport,
            limits=limits,
        )
        return http_client

    def list_models(self, **kwargs):
        api_key = kwargs.pop("api_key", self.api_key)
        host = kwargs.pop("host", self.base_url.host)
        port = kwargs.pop("port", self.base_url.port)
        return HaiModel.list(
            api_key=api_key,
            host=host,
            port=port,
            **kwargs,
        )
    
    def verify_api_key(self, api_key: str = None, **kwargs):
        api_key = api_key or self.api_key
        return self.completions.verify_api_key(api_key, **kwargs)
    
    def request_worker(self, **kwargs):
        return self.completions.request_worker(**kwargs)

    def _process_response(
        self,
        *,
        cast_to: Type[ResponseT],
        options: FinalRequestOptions,
        response: httpx.Response,
        stream: bool,
        stream_cls: type[Stream[Any]] | type[AsyncStream[Any]] | None,
        retries_taken: int = 0,
    ) -> ResponseT:
        if response.request.headers.get(RAW_RESPONSE_HEADER) == "true":
            return cast(
                ResponseT,
                LegacyAPIResponse(
                    raw=response,
                    client=self,
                    cast_to=cast_to,
                    stream=stream,
                    stream_cls=stream_cls,
                    options=options,
                    retries_taken=retries_taken,
                ),
            )

        origin = get_origin(cast_to) or cast_to

        if inspect.isclass(origin) and issubclass(origin, BaseAPIResponse):
            if not issubclass(origin, APIResponse):
                raise TypeError(f"API Response types must subclass {APIResponse}; Received {origin}")

            response_cls = cast("type[BaseAPIResponse[Any]]", cast_to)
            return cast(
                ResponseT,
                response_cls(
                    raw=response,
                    client=self,
                    cast_to=extract_response_type(response_cls),
                    stream=stream,
                    stream_cls=stream_cls,
                    options=options,
                    retries_taken=retries_taken,
                ),
            )

        if cast_to == httpx.Response:
            return cast(ResponseT, response)

        api_response = HAPIResponse(
            raw=response,
            client=self,
            cast_to=cast("type[ResponseT]", cast_to),  # pyright: ignore[reportUnnecessaryCast]
            stream=stream,
            stream_cls=stream_cls,
            options=options,
            retries_taken=retries_taken,
        )
        if bool(response.request.headers.get(RAW_RESPONSE_HEADER)):
            return cast(ResponseT, api_response)

        return api_response.parse()
    

    ### --- 关于DDF Client的函数 --- ###
    ## # --- 关于User的函数 --- ##
    def list_users(self):
        """
        List all users
        Note: Only admin can use this function
        """
        return self.ddf.user.list_users()
    
    def create_user(self, **kwargs):
        """
        Create a new user
        Note: Only admin can use this function
        """
        return self.ddf.user.create_user(**kwargs)
    
    def delete_user(self, user_id: str):
        """
        Delete a user
        Note: Only admin can use this function
        """
        return self.ddf.user.delete_user(user_id=user_id)
    
    ### --- 关于Key的函数 --- ###
    def list_api_keys(self):
        """
        List all keys
        Note: Only admin can use this function
        """
        return self.ddf.key.list_api_keys()
    
    def create_api_key(self, **kwargs):
        """
        Create a new key
        Note: Only admin can use this function
        """
        return self.ddf.key.create_api_key(**kwargs)
    
    def delete_api_key(self, api_key_id: str):
        """
        Delete a key
        Note: Only admin can use this function
        """
        return self.ddf.key.delete_api_key(api_key_id=api_key_id)
    
    def get_remote_model(self, model_name: str):
        """
        Get a remote model
        """
        return self.ddf.worker.get_remote_model(model_name=model_name)