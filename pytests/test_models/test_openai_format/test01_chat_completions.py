import os, sys, time
from pathlib import Path
import json 

here = Path(__file__).parent
repo_root = here.parent.parent.parent
sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")

from hepai import HepAI, Stream, ChatCompletionChunk, ChatCompletion


from pytests.test_models.test_anthropic_format.config import default_config
from pytests.test_models.test_data.error_tool import openai_style_tools, anthropic_style_tools

client = HepAI(
    api_key=default_config.client.api_key, 
    base_url=default_config.client.base_url,
    proxy="http://localhost:4250/"  # set proxy to base_url
)

test_data_file = here.parent / "test_data" / "error_message_openai.json"
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

    response: Stream = client.chat.completions.create(
        model=MODEL,
        messages = messages,
        stream=True,
    )
    print(f"R: ", end="")
    reasoning_flag = True
    i = 0
    full_response = ""
    for chunk in response:
        print(f'{i}: {chunk.model_dump()}', flush=True)
        i += 1
        
        # chunk: ChatCompletionChunk = chunk
        
        # if chunk is None:
        #     continue

        # if reasoning_flag:
        #     if not chunk.choices:
        #         continue
        #     reasoning_content = chunk.choices[0].delta.model_extra.get("reasoning_content", None)
        #     if reasoning_content:  # 有思考过程
        #         print(reasoning_content, end="", flush=True)
        #         continue
        #     if chunk.choices[0].delta.content == "\n\n":
        #         # 思考模式结束
        #         reasoning_flag = False
        #         print(f'A: ', end="")
        #         continue

        # x = chunk.choices[0].delta.content
        # if x:
        #     print(x, end="", flush=True)
        
        # print(chunk)
    
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
    response: Stream = client.chat.completions.create(
        model=MODEL,
        messages = messages,
        stream=False,
    )
    x: ChatCompletion = response
    # print(x.choices[0].message.content)
    print(x)
    elapsed = time.time() - start
    print()
    # print("Full response:\n", content)
    # assert len(content) > 0, "Expected non-empty response from non-stream"
    print()
    print_result("Status", "PASSED ✓")
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