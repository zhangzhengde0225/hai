import os, sys, time
from anthropic import Anthropic
from pathlib import Path

here = Path(__file__).parent
repo_root = here.parent.parent
sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")


## 1
api_key = os.environ["HEPAI_API_KEY"]
# base_url = "https://aiapi.ihep.ac.cn/apiv2"
base_url = "https://aiapi.ihep.ac.cn/apiv2/anthropic/"

api_key = os.getenv("3090_WORKER_API_KEY")
base_url = "http://localhost:42605/apiv2/anthropic/"

api_key = os.environ["HEPAI_API_KEY"]
base_url = "http://localhost:42500/apiv2/anthropic/"

client = Anthropic(
    api_key=api_key,
    base_url=base_url,
)

test_data_file = here / "test_data" / "error_message_minimax.json"
with open(test_data_file, "r") as f:
    messages = eval(f.read())


MODEL = "minimax/minimax-m2.5"
MODEL = "minimax/minimax-m2.5-highspeed"
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
    with client.messages.stream(
        max_tokens=1024,
        messages=messages,
        model=MODEL,
    ) as stream:
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            char_count += len(text)
            full_response += text
    elapsed = time.time() - start
    print(f"\n\nFull response:\n{full_response}")
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
    print()
    print_result("Status", "PASSED ✓")
    print_result("message id", message.id)
    print_result("stop reason", message.stop_reason)
    print_result("input tokens", message.usage.input_tokens)
    print_result("output tokens", message.usage.output_tokens)
    print_result("time elapsed", f"{elapsed:.2f}s")

if __name__ == "__main__":
    print(f"\n{'#' * 60}")
    print(f"  Anthropic Client Test  |  base_url: {base_url}")
    print(f"{'#' * 60}")
    try:
        test_stream()
    except Exception as e:
        print_result("Status", f"FAILED ✗  {e}")
    try:
        test_non_stream()
    except Exception as e:
        print_result("Status", f"FAILED ✗  {e}")
    print(f"\n{SEP}")
    print("  All tests done.")
    print(SEP)