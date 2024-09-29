
import os, sys
import os, sys
from pathlib import Path
here = Path(__file__).parent
try:
    from hepai import HepAI
except:
    sys.path.insert(0, f'{here.parent.parent}')
    from hepai import HepAI
from openai.types.chat import ChatCompletion
from openai import Stream


client = HepAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    proxy="http://localhost:8118",
)

stream = True
response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Sai hello"}],
            stream=stream,
        )
if stream:
    assert isinstance(response, Stream), "stream must be a Stream object"
    full_rst = ""
    for chunk in response:
        char = chunk.choices[0].delta.content
        if char:
            print(char, end="")
            full_rst += char
    print()
else:
    assert type(response, ChatCompletion), "response must be a ChatCompletion object"
    full_rst = response.choices[0].message.content

print(f"rst: {full_rst}")
