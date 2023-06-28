
## 如何通过hepai的API使用GPT-3.5(ChatGPT)

+ 无需openai账号和梯子
+ turbo模型，速度快
+ 需要hepai的api_key

## 安装hepai
```
pip install hepai --upgrade
```
### 安装依赖包
```
pip install opencv-python
pip install pillow
pip install tqdm
```

## 使用

设置环境变量
```bash
export HEPAI_API_KEY=<your api key>
```
联系zdzhang@ihep.ac.cn获取hepai的api_key。

示例代码：
```python

import os, sys
import hai

models = hai.Model.list()  # 列出所有可用模型
print(models)

system_prompt = "You are ChatGPT, answering questions conversationally"
prompt = "Hello!"

result = hai.LLM.chat(
        model='openai/gpt-3.5-turbo',  # 指定可用模型名字
        api_key=os.getenv("HEPAI_API_KEY"),  # 输入hepai_api_key
        messages=[  # 一个会话可能会有对个轮次，messages包含了所有轮次的对话，总是以角色user结束，gpt作为assistant来回复
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
            ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
        ],
        stream=True,
    )
# result是一个流式数据生成器，需要遍历获取全部结果

full_result = ""
for i in result:
    full_result += i
    sys.stdout.write(i)
    sys.stdout.flush()
print()
```


