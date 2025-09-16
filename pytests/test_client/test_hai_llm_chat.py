

from pathlib import Path
import unittest
here = Path(__file__).parent
import os, sys
try:
    from hepai import HepAI
except:
    sys.path.insert(1, str(here.parent.parent))
    from hepai import HepAI


import hepai
import hai
hai.api_key = os.environ.get('HEPAI_API_KEY')

def request_model(prompt='hello', system_prompt=None):
    system_prompt = system_prompt if system_prompt else "Answering questions conversationally"

    result = hai.LLM.chat(
            model='openai/gpt-4o',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
                ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
            ],
            stream=True,
        )

    full_result = ""
    for i in result:
        full_result += i
        sys.stdout.write(i)
        sys.stdout.flush()
    print()
    return full_result

answer = request_model(prompt='hello')

