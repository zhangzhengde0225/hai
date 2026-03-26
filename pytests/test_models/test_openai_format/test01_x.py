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

test_data_file = here.parent / "test_data" / "error_chat_tool_call_round1.json"

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


def test_non_stream():
    print_section("TEST 2: Non-Streaming Response")
    print_result("Model", MODEL)
    print_result("Status", "RUNNING...")
    start = time.time()

    rounds = 1
    while rounds <= 2:
        response: Stream = client.chat.completions.create(
            model=MODEL,
            messages = messages,
            stream=False,
            tools=openai_style_tools,
        )
        x: ChatCompletion = response
        # print(x.choices[0].message.content)
        print(f"Round[{rounds:0>2}] Response:\n", x)

        rounds += 1
        break

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