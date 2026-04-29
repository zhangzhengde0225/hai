import os, sys, time
from anthropic import Anthropic
from pathlib import Path
import json 

here = Path(__file__).parent
repo_root = here.parent.parent.parent
sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")


from pytests.test_models.test_anthropic_format.config import default_config


client = Anthropic(
    api_key=default_config.client.api_key,
    base_url=default_config.client.base_url,
)

test_data_file = here.parent / "test_data" / "error_message_minimax.json"
with open(test_data_file, "r") as f:
    messages = eval(f.read())


MODEL = default_config.model
SEP = "=" * 60

def print_section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def print_result(label, value):
    print(f"  [{label}] {value}")

def test_stream():
    print_section("TEST 1: Streaming Response")
    print_result("Model", MODEL)
    print_result("Status", "RUNNING...")
    print()
    start = time.time()
    char_count = 0
    print("Streaming Response:")

    stream = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system="You are a helpful assistant.",
            messages=messages,
            stream=True,
        )
    
    reasoning_buffer = ""
    text_buffer = ""
    tool_buffer = ""

    for chunk in stream:
        if chunk.type == "content_block_start":
            if hasattr(chunk, "content_block") and chunk.content_block:
                if chunk.content_block.type == "text":
                    print("\n" + "=" * 60)
                    print("Response Content:")
                    print("=" * 60)
                elif chunk.content_block.type == "thinking":
                    print("\n" + "=" * 60)
                    print("Thinking:")
                    print("=" * 60)
                elif chunk.content_block.type == "tool_use":
                    print("\n" + "=" * 60)
                    print("Tool Use:")
                    print("=" * 60)

        elif chunk.type == "content_block_delta":
            if hasattr(chunk, "delta") and chunk.delta:
                if chunk.delta.type == "thinking_delta":
                    # 流式输出 thinking 过程
                    new_thinking = chunk.delta.thinking
                    if new_thinking:
                        print(new_thinking, end="", flush=True)
                        reasoning_buffer += new_thinking
                elif chunk.delta.type == "text_delta":
                    # 流式输出文本内容
                    new_text = chunk.delta.text
                    if new_text:
                        print(new_text, end="", flush=True)
                        text_buffer += new_text
                elif chunk.delta.type == "input_json_delta":
                    new_json = chunk.delta.partial_json
                    if new_json:
                        print(new_json, end="", flush=True)
                        tool_buffer += new_json
        else:
            pass
    
    tool_buffer = json.loads(tool_buffer) if tool_buffer else {}

    full_response = f'{reasoning_buffer}\n{tool_buffer}\n{text_buffer}'
    elapsed = time.time() - start
    print(f"\n\nFull response:\n{full_response}")
    assert len(full_response) > 0, "Expected non-empty response from stream"
    print()
    print()
    print_result("Status", "PASSED ✓")
    print_result("chars received", char_count)
    print_result("time elapsed", f"{elapsed:.2f}s")

def test_non_stream():
    print_section("TEST 2: Non-Streaming Response")
    print_result("Model", MODEL)
    print_result("Status", "RUNNING...")
    start = time.time()
    message = client.messages.create(
        max_tokens=1024,
        messages=messages,
        model=MODEL,
    )
    
    elapsed = time.time() - start
    content = message.content if message.content else ""
    print()
    print("Full response:\n", content)
    assert len(content) > 0, "Expected non-empty response from non-stream"
    print()
    print_result("Status", "PASSED ✓")
    print_result("message id", message.id)
    print_result("stop reason", message.stop_reason)
    print_result("input tokens", message.usage.input_tokens)
    print_result("output tokens", message.usage.output_tokens)
    print_result("time elapsed", f"{elapsed:.2f}s")

if __name__ == "__main__":
    print(f"\n{'#' * 60}")
    print(f"  Anthropic Client Test  |  base_url: {default_config.client.base_url}")
    print(f"{'#' * 60}")
    # try:
    #     test_stream()
    # except Exception as e:
    #     print_result("Status", f"FAILED ✗  {e} ")
    try:
        test_non_stream()
    except Exception as e:
        print_result("Status", f"FAILED ✗  {e} ")
    print(f"\n{SEP}")
    print("  All tests done.")
    print(SEP)