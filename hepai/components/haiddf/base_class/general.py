from typing import Dict, List
import time
import json


async def convert_claude_to_openai_format(response: Dict) -> Dict:
    """将claude系列模型的返回结果转换为OpenAI格式"""
    # 这里根据实际的claude模型返回结果结构进行适配
    
    # 转换msg
    choices = []
    for i, msg in enumerate(response.get("content")):
        oai_msg = {
            "index": i,
            "message": {
                "role": response.get("role", "user"),
                "content": msg.get("text", ""),
                "refusal": None,
                "annotations": msg.get("citations"),
            },
            "logprobs": None,
            "finish_reason": response.get("finish_reason"),
        }
        choices.append(oai_msg)
    
    # 不转换usage
  
    openai_format = {
        "id": response.get("id"),
        "object": "chat.completion",
        "created": time.time(),
        "model": response.get("model"),
        "choices": choices,
        "usage": response.get("usage", {}),
        "service_tier": response.get("usage", {}).get("service_tier", None)
    }
    return openai_format


async def convert_object_openai_to_anthropic(openai_obj):
    from openai.types.chat import (
        ChatCompletion, ChatCompletionMessageToolCall
    )
    from openai.types import CompletionUsage
 
    assert isinstance(openai_obj, ChatCompletion), "openai_obj must be an instance of ChatCompletion"
    
    from anthropic.types import (
        Usage, Message, 
        TextBlock, ThinkingBlock, RedactedThinkingBlock, ToolUseBlock,
        ServerToolUseBlock, WebSearchToolResultBlock
    )

    role = None
    content = []
    stop_reason = None

    
    choices = openai_obj.choices
    for choice in choices:
        finish_reason = choice.finish_reason
        msg = choice.message
        if role is None:
            role = msg.role

        if finish_reason == "tool_calls":
            stop_reason = "tool_use"
            tool_calls: List[ChatCompletionMessageToolCall] = msg.tool_calls
            for tool_call in tool_calls:
                tool_use_block = ToolUseBlock(
                    id=tool_call.id,
                    input=tool_call.function.arguments,
                    name=tool_call.function.name,
                    type="tool_use"  # function -> tool_use
                )
                content.append(tool_use_block)
        elif finish_reason == "stop":
            stop_reason = "end_turn"
            text_block = TextBlock(
                text=msg.content,
                citations=msg.annotations,
                type="text"
            )
            content.append(text_block)
        else:
            raise NotImplementedError("Only tool_calls finish_reason is implemented in this conversion.")

    
    usage: CompletionUsage = openai_obj.usage
    
    anthropic_usage = Usage(
        cache_creation_input_tokens=usage.prompt_tokens_details.cached_tokens if usage and usage.prompt_tokens_details else None,
        cache_read_input_tokens=None,
        input_tokens=usage.prompt_tokens if usage else None,
        output_tokens=usage.completion_tokens if usage else None,
        server_tool_use=None,
        service_tier=None
    )
    
    message = Message(
        id=openai_obj.id,
        content=content,
        model=openai_obj.model,
        role=role,
        stop_reason=stop_reason,
        stop_sequence=None,
        type="message",
        usage=anthropic_usage
    )
    
    return message


async def convert_openai_to_anthropic_format(response: Dict) -> Dict:
    """
    将OpenAI格式的返回结果转换为Anthropic(Claude)格式
    """
    # 解析choices
    content = []
    role = None
    finish_reason = None

    choices = response.get("choices", [])
    for choice in choices:
        msg = choice.get("message", {})
        # 只取第一个role
        if role is None:
            role = msg.get("role", "user")
        finish_reason = choice.get("finish_reason")
        content.append({
            "text": msg.get("content", ""),
            "citations": msg.get("annotations", None),
            "type": "text",
        })
        
    # 转换usage
    usage = response.get("usage", {})
    # "# cache_creation_input_tokens=None, cache_read_input_tokens=None, input_tokens=None, output_tokens=None, server_tool_use=None, service_tier=None, c"
    anthropic_usage = {
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "input_tokens": usage.get("prompt_tokens", None),
        "output_tokens": usage.get("completion_tokens", None),
        "server_tool_use": None,
        "service_tier": response.get("service_tier", None),
    }

    anthropic_format = {
        "id": response.get("id"),
        "model": response.get("model"),
        "role": role,
        "content": content,
        "stop_reason": finish_reason,
        "stop_sequence": None,
        "type": "message",
        "usage": anthropic_usage
    }
    return anthropic_format


async def convert_openai_to_anthropic_format_stream(generator, return_dict=True):

    if return_dict:
        async for chunk in convert_openai_to_anthropic_format_stream_chunk(generator):
            yield {
                "event": chunk.get("type"),
                "data": chunk
            }
    else:
        async for chunk in convert_openai_to_anthropic_format_stream_chunk(generator):
            yield f"event: {chunk.get('type')}\ndata: {json.dumps(chunk)}\n\n"

async def convert_openai_to_anthropic_format_stream_chunk(generator):
    """将 OpenAI 流式输出转换为 Anthropic 格式"""

    first_chunk = True
    accumulated_content = ""
    message_id = None
    model = None
    usage_info = None
    content_finished = False
    tool_calls_data = {}  # 存储工具调用数据 {index: {id, name, arguments}}
    current_content_index = 0

    # i = 0
    async for chunk in generator:
        if not chunk:
            continue
        # print(f"{i}: {chunk}")
        # i += 1
        if not isinstance(chunk, dict):
            chunk = chunk.model_dump()

        # 提取基本信息
        if message_id is None:
            message_id = chunk.get('id')
        if model is None:
            model = chunk.get('model')

        # 保存 usage 信息
        if chunk.get('usage'):
            usage_info = chunk.get('usage')

        choices = chunk.get('choices', [])
        if not choices:
            # 如果没有 choices，但有 usage，说明是最后的 usage chunk
            if usage_info and (content_finished or tool_calls_data):
                # 确定停止原因
                stop_reason = 'tool_use' if tool_calls_data else 'end_turn'

                yield {
                    'delta': {
                        'stop_reason': stop_reason,
                        'stop_sequence': None
                    },
                    'type': 'message_delta',
                    'usage': {
                        'cache_creation_input_tokens': 0,
                        'cache_read_input_tokens': 0,
                        'input_tokens': usage_info.get('prompt_tokens', 0),
                        'output_tokens': usage_info.get('completion_tokens', 0),
                        'server_tool_use': None
                    }
                }

                # 构建内容列表
                content_list = []
                if accumulated_content:
                    content_list.append({
                        'citations': None,
                        'text': accumulated_content,
                        'type': 'text'
                    })

                # 添加工具调用内容
                for tool_data in tool_calls_data.values():
                    try:
                        # 尝试解析 JSON 参数
                        parsed_args = json.loads(tool_data['arguments']) if tool_data['arguments'] else {}
                    except:
                        parsed_args = tool_data['arguments']

                    content_list.append({
                        'id': tool_data['id'],
                        'input': parsed_args,
                        'name': tool_data['name'],
                        'type': 'tool_use'
                    })

                yield {
                    'type': 'message_stop',
                    'message': {
                        'id': message_id,
                        'content': content_list,
                        'model': model,
                        'role': 'assistant',
                        'stop_reason': stop_reason,
                        'stop_sequence': None,
                        'type': 'message',
                        'usage': {
                            'cache_creation_input_tokens': 0,
                            'cache_read_input_tokens': 0,
                            'input_tokens': usage_info.get('prompt_tokens', 0),
                            'output_tokens': usage_info.get('completion_tokens', 0),
                            'server_tool_use': None,
                            'service_tier': None
                        }
                    }
                }
            continue

        choice = choices[0]  # 只处理第一个choice
        delta = choice.get('delta', {})
        finish_reason = choice.get('finish_reason')

        # 第一个chunk：发送 message_start
        if first_chunk:
            yield {
                'message': {
                    'id': message_id,
                    'content': [],
                    'model': model,
                    'role': 'assistant',
                    'stop_reason': None,
                    'stop_sequence': None,
                    'type': 'message',
                    'usage': {
                        'cache_creation_input_tokens': 0,
                        'cache_read_input_tokens': 0,
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'server_tool_use': None,
                        'service_tier': None
                    }
                },
                'type': 'message_start'
            }
            first_chunk = False

        # 处理内容增量
        content = delta.get('content', '')
        if content and not tool_calls_data:  # 如果有工具调用就不处理文本内容
            if accumulated_content == "":  # 第一次文本内容
                yield {
                    'content_block': {
                        'citations': None,
                        'text': '',
                        'type': 'text'
                    },
                    'index': current_content_index,
                    'type': 'content_block_start'
                }

            accumulated_content += content

            yield {
                'delta': {
                    'text': content,
                    'type': 'text_delta'
                },
                'index': current_content_index,
                'type': 'content_block_delta'
            }

            yield {
                'type': 'text',
                'text': content,
                'snapshot': accumulated_content
            }

        # 处理tool_calls增量
        tool_calls = delta.get('tool_calls', [])
        if tool_calls is not None:
            for tool_call in tool_calls:
                tool_index = tool_call.get('index', 0)
                tool_id = tool_call.get('id')
                function_info = tool_call.get('function', {})

                # 初始化工具调用数据
                if tool_index not in tool_calls_data:
                    tool_calls_data[tool_index] = {
                        'id': tool_id or '',
                        'name': function_info.get('name', ''),
                        'arguments': ''
                    }

                    # 发送 content_block_start 事件
                    content_index = len(tool_calls_data) - 1 + (1 if accumulated_content else 0)
                    yield {
                        'content_block': {
                            'id': tool_calls_data[tool_index]['id'],
                            'input': {},
                            'name': tool_calls_data[tool_index]['name'],
                            'type': 'tool_use'
                        },
                        'index': content_index,
                        'type': 'content_block_start'
                    }

                # 更新工具调用数据
                if tool_id:
                    tool_calls_data[tool_index]['id'] = tool_id
                if function_info.get('name'):
                    tool_calls_data[tool_index]['name'] = function_info.get('name')
                if function_info.get('arguments'):
                    tool_calls_data[tool_index]['arguments'] += function_info.get('arguments')

                    # 发送 input_json 增量事件
                    content_index = len(tool_calls_data) - 1 + (1 if accumulated_content else 0)

                    yield {
                        'delta': {
                            'partial_json': function_info.get('arguments'),
                            'type': 'input_json_delta'
                        },
                        'index': content_index,
                        'type': 'content_block_delta'
                    }

                    # 尝试解析当前的 JSON 状态
                    try:
                        current_json = json.loads(tool_calls_data[tool_index]['arguments'])
                    except:
                        current_json = {}

                    yield {
                        'type': 'input_json',
                        'partial_json': function_info.get('arguments'),
                        'snapshot': current_json
                    }

        # 处理结束
        if finish_reason == 'stop':
            if accumulated_content:
                yield {
                    'index': 0,
                    'type': 'content_block_stop',
                    'content_block': {
                        'citations': None,
                        'text': accumulated_content,
                        'type': 'text'
                    }
                }
            content_finished = True
        elif finish_reason == 'tool_calls':
            # 为每个工具调用发送 content_block_stop
            for idx, tool_data in tool_calls_data.items():
                try:
                    parsed_args = json.loads(tool_data['arguments']) if tool_data['arguments'] else {}
                except:
                    parsed_args = tool_data['arguments']

                content_index = idx + (1 if accumulated_content else 0)
                yield {
                    'index': content_index,
                    'type': 'content_block_stop',
                    'content_block': {
                        'id': tool_data['id'],
                        'input': parsed_args,
                        'name': tool_data['name'],
                        'type': 'tool_use'
                    }
                }

async def convert_input_anthropic_to_openai_format(request_body: Dict) -> Dict:
    """
    将Anthropic风格的输入参数转换为OpenAI风格的输入参数
    """
    # 1. messages转换
    messages = []
    for msg in request_body.get("messages", []):
        role = msg.get("role")
        content = msg.get("content")
        # content 可能是字符串或content block数组
        if isinstance(content, str):
            messages.append({"role": role, "content": content})
        elif isinstance(content, list):
            ctnt = ""
            for block in content:
                block_type = block.get("type")
                if block_type == "text":
                    text_content = block.get("text", "")
                    ctnt += f"\n{text_content}"
                elif block_type == "tool_use":
                    # ctnt += f"\n[Use Tool: {block.get('name')} with input {block.get('input')}]"
                    ctnt += f"\n{block}]"
                elif block_type == "tool_result":
                    # ctnt += f"\n[Tool Result: {block.get('name')} output {block.get('content')}]"
                    ctnt += f"\n{block}]"
                else:
                    # ctnt += f"\n{block}]"  # 直接转换为字符串
                    raise NotImplementedError(f"Block type {block_type} not implemented in conversion.")
            messages.append({"role": role, "content": ctnt})
        else:
            messages.append({"role": role, "content": ""})

    # 2. model
    model = request_body.get("model")
    # 3. max_tokens
    max_tokens = request_body.get("max_tokens")
    # 4. temperature
    temperature = request_body.get("temperature")
    # 5. top_p
    top_p = request_body.get("top_p")
    # 6. stop_sequences -> stop
    stop = request_body.get("stop_sequences")
    # 7. metadata
    metadata = request_body.get("metadata")
    # 8. service_tier
    service_tier = request_body.get("service_tier")
    # 9. stream
    stream = request_body.get("stream")
    # 10. tools
    tools = request_body.get("tools")
    # 很复杂的转换：
    oai_tools = []
    if tools:
        for i, tool in enumerate(tools):
            input_schema = tool.get("input_schema", {})
            oai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "parameters": input_schema,
                    # "strict": True,
                }
            }
            oai_tools.append(oai_tool)

    # 11. tool_choice
    tool_choice = request_body.get("tool_choice")
    # 12. system prompt
    system = request_body.get("system")
    if system:
        # 多条system合并为一条
        system_list = [x["text"] for x in system if isinstance(x, dict) and "text" in x]
        _system_text = "\n".join(system_list)

        # OpenAI的system prompt是messages的第一条
        messages = [{"role": "system", "content": _system_text}] + messages

    # 构造OpenAI格式
    openai_body = {
        "model": model,
        "messages": messages,
    }
    if max_tokens is not None:
        openai_body["max_completion_tokens"] = max_tokens
    if temperature is not None:
        openai_body["temperature"] = temperature
    if top_p is not None:
        openai_body["top_p"] = top_p
    if stop is not None:
        openai_body["stop"] = stop
    if metadata is not None:
        openai_body["metadata"] = metadata
    if service_tier is not None:
        openai_body["service_tier"] = service_tier
    if stream is not None:
        openai_body["stream"] = stream
    if oai_tools:
        openai_body["tools"] = oai_tools
    if tool_choice is not None:
        openai_body["tool_choice"] = tool_choice

    return openai_body