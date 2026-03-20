
import os, sys, time
from anthropic import Anthropic
import json

client = Anthropic(
    api_key=os.getenv("HEPAI_API_KEY"),
    base_url="https://aiapi.ihep.ac.cn/apiv2/anthropic/",
    )
MODEL = "minimax/minimax-m2.7-highspeed"

def test_messages():
    messages = [
        {
            "role": "user",
            "name": "user",
            "content": "你跟我看看agflow_knowledge. skill中有哪些脚本1"
        },
        {
            "role": "assistant",
            "content": "<think>\n用户想要查看 ragflow_knowledge skill 中的脚本。我需要先加载这个skill来查看其内容。\n</think>\n\n\n[{'id': 'call_function_c5f7zog7g35l_1', 'function': {'arguments': '{\"skill\": \"ragflow_knowledge\"}', 'name': 'Skill'}, 'type': 'function'}]"
        },
        {
            "role": "user",
            "name": "user",
            "content": "Skill for ragflow_knowledge: <skill-loaded name=\"ragflow_knowledge\">\n    # Skill: ragflow_knowledge\n\n# RAGFlow知识库与PDF文件管理\n\n## 何时使用\n\n1. 用户需要学习RAGFlow知识库的构建与配置过程。\n2. 需要将本地PDF、Markdown文件等文件上传到RAGFlow知识库、更新知识库文档与元数据。\n3. 需要处理PDF论文、PDF手册、长文档手册，上传到RAGFlow知识库进行长文档混合检索等操作。\n\n## 核心功能与工作流程\n\n### 功能1：RAGFlow知识库的构建与配置\n\n指导RAGFlow知识库的构建与配置过程，具体见`references`目录下的`ragflow_config.md`。\n\n### 功能2：PDF文件的清洗与上传处理\n\n在用户需要将PDF文件的解析为markdown文本、清洗后上传到RAGFlow知识库进行混合检索时，可以使用此功能。具体的工作流程为：\n\n1. 询问用户的PDF文件的清洗需求：是直接解析整篇文档作为一个文件进行混合检索，还是需要长文档的分逐页割，按照逐页进行解析后检索。\n2. 用户说明了解析清洗要求后，必须阅读见`references`目录下的`pdf_process.md`文件，根据用户的分割解析需求，使用合适的脚本进行处理。\n3. PDF分割清洗后先确认分割后文件的绝对路径，以便后面进行处理。\n4. 使用对应的脚本进行分割后PDF文件的解析，转化为对应的markdown文件。因为使用Mineru模型进行解析，速度较慢，因此都推荐使用后台模式进行解析。\n5. 要求用户构建对应的目录文件，方便后面进行目录摘要的总结，具体目录文件的构建方法阅读`references`目录下的`content_process.md`文件。这一步通常需要要求用户来仔细核对，确定文件总结的具体参数。\n6. 然后参考`ragflow_config.md`，上传到RAGFlow知识库，进行检索测试。\n\n### 功能3：markdown文件的清洗与上传处理\n\n如果是纯markdown文件格式长文档，有明确的页数对应，则可以参考功能2，直接跳过1-4，直接构建目录文件，然后进行上传和检索。\n\n**Available resources in /home/xiongdb/b9agent/runs/xiongdb@ihep.ac.cn/configs/skills/ragflow_knowledge:**\n- Scripts: pdf_split_script.py, ragflow_process.py, pdf_manual_parse_script.py, pdf_manual_rag_process.py, pdf_parse_script.py, check_ragflow.py, .env, __pycache__, pdf_manual_content_processor.py, pdf_manual_search.py\n- References: ragflow_config.md, content_process.md, pdf_process.md\n    </skill-loaded>\n\n    Follow the instructions in the skill above to complete the user's task."
        },
        {
            "role": "assistant",
            "content": "<think>\n用户想查看ragflow_knowledge skill中的脚本列表。根据skill加载后的信息，我可以看到在\"Available resources\"部分已经列出了脚本列表。让我整理一下这些脚本信息：\n\nScripts:\n- pdf_split_script.py\n- ragflow_process.py\n- pdf_manual_parse_script.py\n- pdf_manual_rag_process.py\n- pdf_parse_script.py\n- check_ragflow.py\n- .env\n- __pycache__\n- pdf_manual_content_processor.py\n- pdf_manual_search.py\n\n这些是ragflow_knowledge skill中包含的脚本。我可以直接告诉用户这些信息。\n</think>\n\n根据加载的 `ragflow_knowledge` skill，其中包含的脚本列表如下：\n\n## Scripts 列表\n\n| 脚本名称 | 说明 |\n|---------|------|\n| `pdf_split_script.py` | PDF分割脚本 |\n| `ragflow_process.py` | RAGFlow处理脚本 |\n| `pdf_manual_parse_script.py` | PDF手册解析脚本 |\n| `pdf_manual_rag_process.py` | PDF手册RAG处理脚本 |\n| `pdf_parse_script.py` | PDF解析脚本 |\n| `check_ragflow.py` | RAGFlow检查脚本 |\n| `pdf_manual_content_processor.py` | PDF手册内容处理脚本 |\n| `pdf_manual_search.py` | PDF手册搜索脚本 |\n\n其他文件：\n- `.env` - 环境变量配置\n- `__pycache__` - Python缓存目录\n\n## References 参考文档\n\n- `ragflow_config.md` - RAGFlow配置说明\n- `content_process.md` - 内容处理说明  \n- `pdf_process.md` - PDF处理说明\n\n需要我查看某个具体脚本的内容吗？"
        },
        {
            "role": "user",
            "name": "user_proxy",
            "content": "再跟我查看ragflow_process.py文件的内容"
        }
    ]
    return messages

def test_antropic_style_tools():
    anthropic_style_tools = [
{'name': 'pdf_manual_search',
  'input_schema': {'properties': {'question': {'description': 'question',
                                               'title': 'Question',
                                               'type': 'string'},
                                  'max_items': {'default': 5,
                                                'description': 'max_items',
                                                'title': 'Max Items',
                                                'type': 'integer'},
                                  'similarity_threshold': {'default': 0.2,
                                                           'description': 'similarity_threshold',
                                                           'title': 'Similarity Threshold',
                                                           'type': 'number'}},
                   'required': ['question'],
                   'type': 'object'},
  'description': '\n'
                 '    该函数通过匹配输入问题相近的文档目录及其对应的文件markdown文件位置，帮助进行下一步文档的仔细阅读\n'
                 '    Arguments:\n'
                 '        question: The question to search for.\n'
                 '        max_items: The maximum number of items to return.\n'
                 '        similarity_threshold: The similarity threshold for filtering results.\n'
                 '    '},
 {'name': 'run_bash',
  'input_schema': {'properties': {'cmd': {'description': 'cmd', 'title': 'Cmd', 'type': 'string'}},
                   'required': ['cmd'],
                   'type': 'object'},
  'description': 'Execute shell command in workspace directory.\n'
                 '\n'
                 '        The working directory persists across calls: cd commands take effect\n'
                 '        for subsequent invocations, as long as the target stays within the\n'
                 '        allowed workspace.\n'
                 '        '},
 {'name': 'run_read',
  'input_schema': {'properties': {'path': {'description': 'path',
                                           'title': 'Path',
                                           'type': 'string'},
                                  'minilimit': {'default': None,
                                                'description': 'minilimit',
                                                'title': 'Minilimit',
                                                'type': 'integer'},
                                  'maxlimit': {'default': -1,
                                               'description': 'maxlimit',
                                               'title': 'Maxlimit',
                                               'type': 'integer'}},
                   'required': ['path'],
                   'type': 'object'},
  'description': '\n'
                 '        Read file contents.\n'
                 '        \n'
                 '        Args:\n'
                 '            path : Path to file.\n'
                 '            minilimit : The start of  Maximum number of lines to read.\n'
                 '            maxlimit : The end of  Maximum number of lines to read.\n'
                 '        '},
 {'name': 'run_write',
  'input_schema': {'properties': {'path': {'description': 'path',
                                           'title': 'Path',
                                           'type': 'string'},
                                  'content': {'description': 'content',
                                              'title': 'Content',
                                              'type': 'string'}},
                   'required': ['path', 'content'],
                   'type': 'object'},
  'description': 'Write content to file.'},
 {'name': 'run_edit',
  'input_schema': {'properties': {'path': {'description': 'path',
                                           'title': 'Path',
                                           'type': 'string'},
                                  'old_text': {'description': 'old_text',
                                               'title': 'Old Text',
                                               'type': 'string'},
                                  'new_text': {'description': 'new_text',
                                               'title': 'New Text',
                                               'type': 'string'}},
                   'required': ['path', 'old_text', 'new_text'],
                   'type': 'object'},
  'description': 'Replace exact text in file.'},
 {'name': 'retreve_from_memory',
  'input_schema': {'properties': {'question': {'description': 'question',
                                               'title': 'Question',
                                               'type': 'string'},
                                  'document_ids': {'default': [],
                                                   'description': 'document_ids',
                                                   'items': {'type': 'string'},
                                                   'title': 'Document Ids',
                                                   'type': 'array'},
                                  'page_size': {'default': 10,
                                                'description': 'page_size',
                                                'title': 'Page Size',
                                                'type': 'integer'},
                                  'similarity_threshold': {'default': 0.2,
                                                           'description': 'similarity_threshold',
                                                           'title': 'Similarity Threshold',
                                                           'type': 'number'},
                                  'vector_similarity_weight': {'default': 0.3,
                                                               'description': 'vector_similarity_weight',
                                                               'title': 'Vector Similarity Weight',
                                                               'type': 'number'},
                                  'top_k': {'default': 1024,
                                            'description': 'top_k',
                                            'title': 'Top K',
                                            'type': 'integer'},
                                  'rerank_id': {'default': 'hepai/bge-reranker-v2-m3___OpenAI-API@OpenAI-API-Compatible',
                                                'description': 'rerank_id',
                                                'title': 'Rerank Id',
                                                'type': 'string'},
                                  'keyword': {'default': True,
                                              'description': 'keyword',
                                              'title': 'Keyword',
                                              'type': 'boolean'},
                                  'cross_languages': {'default': ['English', 'Chinese'],
                                                      'description': 'cross_languages',
                                                      'items': {'type': 'string'},
                                                      'title': 'Cross Languages',
                                                      'type': 'array'},
                                  'metadata_condition': {'anyOf': [{'additionalProperties': {'type': 'string'},
                                                                    'type': 'object'},
                                                                   {'type': 'null'}],
                                                         'default': None,
                                                         'description': 'metadata_condition',
                                                         'title': 'Metadata Condition'}},
                   'required': ['question'],
                   'type': 'object'},
  'description': 'Retrieve relevant information from memory. No special requirements, just input '
                 'the question.\n'
                 '        \n'
                 '        Arguments:\n'
                 '            question: The question to retrieve relevant information.\n'
                 '            document_ids: The document_ids to retrieve relevant information. '
                 'Default is [].\n'
                 '            page_size: The number of chunks to retrieve. Default is 10.\n'
                 '            similarity_threshold: The similarity threshold. Default is 0.2.\n'
                 '            vector_similarity_weight: The vector similarity weight. Default is '
                 '0.3.\n'
                 '            top_k: The top_k. Default is 1024.\n'
                 '            rerank_id: The rerank_id. Default is '
                 '"hepai/bge-reranker-v2-m3___OpenAI-API@OpenAI-API-Compatible".\n'
                 '            keyword: Whether to use keyword. Default is True.\n'
                 '            cross_languages: The cross_languages. Default is ["English", '
                 '"Chinese"].\n'
                 '        \n'
                 '        Return:\n'
                 '                The string of relevant information.\n'
                 '        '},
 {'name': 'summry_conversation_to_memory',
  'input_schema': {'properties': {'summary_task_prompt': {'anyOf': [{'type': 'string'},
                                                                    {'type': 'null'}],
                                                          'default': None,
                                                          'description': 'summary_task_prompt',
                                                          'title': 'Summary Task Prompt'}},
                   'required': [],
                   'type': 'object'},
  'description': "Summarize the conversation by user's prompt.\n"
                 '        \n'
                 '        Arguments:\n'
                 "            summary_task_prompt: The user's request for summarizing the "
                 'conversation.\n'
                 '        \n'
                 '        Note:\n'
                 '            If the specific summarizing request is not provided , the default '
                 'prompt will be used.\n'
                 '        '},
 {'name': 'UpdateUserConfig',
  'input_schema': {'properties': {'user_name': {'type': 'string',
                                                'description': "User's name for personalized "
                                                               'addressing'},
                                  'agent_name': {'type': 'string',
                                                 'description': "Assistant's name as preferred by "
                                                                'the user'},
                                  'ask_before_plan': {'type': 'boolean',
                                                      'description': 'Whether to show the plan and '
                                                                     'ask for user approval before '
                                                                     'executing complex tasks'}},
                   'required': [],
                   'type': 'object'},
  'description': 'Update user profile configuration including name, and assistant settings.\n'
                 '\n'
                 'Use this tool when the user wants to:\n'
                 '- Change their name or how they want to be addressed\n'
                 "- Update the assistant's name\n"
                 '- Configure whether to ask before planning tasks\n'
                 '\n'
                 'You can update one or multiple fields at once. Only provide the fields that need '
                 'to be updated.'},
 {'name': 'Skill',
  'input_schema': {'properties': {'skill': {'type': 'string',
                                            'description': 'Name of the skill to load'}},
                   'required': ['skill'],
                   'type': 'object'},
  'description': 'Load a skill to gain specialized knowledge for a task.\n'
                 '\n'
                 'Available skills:\n'
                 '- ragflow_knowledge: '
                 '指导用户如何处理PDF格式的文献、使用RAGFlow矢量知识库框架进行个人的文献管理。当用户提到如何使用RAGFlow、如何上传PDF到RAGFlow知识库、如何处理长文档进行混合检索时立即使用此技能。\n'
                 '- research-paper-writer: Creates formal academic research papers following '
                 'IEEE/ACM formatting standards with proper structure, citations, and scholarly '
                 'writing style. Use when the user asks to write a research paper, academic paper, '
                 'or conference paper on any topic.\n'
                 '- skill-creator: Create new skills, modify and improve existing skills, and '
                 'measure skill performance. Use when users want to create a skill from scratch, '
                 'edit, or optimize an existing skill, run evals to test a skill, benchmark skill '
                 "performance with variance analysis, or optimize a skill's description for better "
                 'triggering accuracy.\n'
                 '- user_system_config: '
                 '修改和更新用户的个人画像、系统提示词、工具偏好配置等。在用户需要调整自己的昵称、智能助手的回复性格、工作流程等系统提示词、工具使用偏好等情况时使用。\n'
                 '- academic-writing: You are an academic writing expert specializing in scholarly '
                 'papers, literature reviews, research methodology, and thesis writing. You must '
                 'adhere to strict academic standards in all outputs.## Core Requirements1. '
                 '**Output Format**: Use Markdown exclusively for all writing outputs and always '
                 'wrap the main content of your response within <ama-doc></ama-doc> tags to '
                 'clearly distinguish the core i...\n'
                 '- update_tools: 指导如何更新智能助手的mcp、函数工具列表。\n'
                 '- academic-writing-refiner: Refine academic writing for computer science '
                 'research papers targeting top-tier venues (NeurIPS, ICLR, ICML, AAAI, IJCAI, '
                 'ACL, EMNLP, NAACL, CVPR, WWW, KDD, SIGIR, CIKM, and similar). Use this skill '
                 'whenever a user asks to improve, polish, refine, edit, or proofread academic or '
                 'research writing — including paper drafts, abstracts, introductions, related '
                 'work sections, methodology descriptions, experiment write-ups, or conclusion '
                 'sections. Also trigger when users paste LaTeX content and ask for writing help, '
                 'mention "camera-ready", "rebuttal", "paper revision", or reference any academic '
                 'venue or conference. This skill handles both full paper refinement and '
                 'section-by-section editing.\n'
                 '- pdf_manual_search: 基于pdf_manual_search工具的手册检索教程，可以查询《spec - X-Ray Diffraction '
                 'Software》，OpenDrSai智能体开发等手册内容。\n'
                 '- download_github_skills: 指导智能体如何从给定的github仓库路径中下载指定的skill文件夹安装到用户的skills目录中。\n'
                 '- update_subagent: 指导如何更新智能助手的子智能体(subagent)的列表。\n'
                 '\n'
                 'When to use:\n'
                 '- IMMEDIATELY when user task matches a skill description\n'
                 '- Before attempting domain-specific work (PDF, MCP, etc.)\n'
                 '\n'
                 'The skill content will be injected into the conversation, giving you\n'
                 'detailed instructions and access to resources.'},
 {'name': 'Task',
  'input_schema': {'properties': {'description': {'type': 'string',
                                                  'description': 'Short task description (3-5 '
                                                                 'words)'},
                                  'prompt': {'type': 'string',
                                             'description': 'The specific tasks that need to be '
                                                            'executed by the sub agent. If the '
                                                            'tasks include code blocks, files, '
                                                            'etc. that need to be executed, they '
                                                            'must be filled in completely.'},
                                  'agent_type': {'type': 'string',
                                                 'enum': ['explore',
                                                          'coder',
                                                          'coder_executor',
                                                          'plan']}},
                   'required': ['description', 'prompt', 'agent_type'],
                   'type': 'object'},
  'description': 'Spawn a subagent for a focused subtask.\n'
                 '\n'
                 'Agent types:\n'
                 '- explore: Read-only agent for exploring code, finding files, searching\n'
                 '- coder: Full agent for writing codes, implementing features and fixing bugs\n'
                 '- coder_executor: A computer terminal that performs no other action than running '
                 'Python scripts (provided to it quoted in ```python code blocks), or sh shell '
                 'scripts (provided to it quoted in ```sh code blocks).\n'
                 '- plan: Planning agent for designing implementation strategies'},
 {'name': 'TodoWrite',
  'input_schema': {'properties': {'items': {'type': 'array',
                                            'items': {'type': 'object',
                                                      'properties': {'content': {'type': 'string'},
                                                                     'status': {'type': 'string',
                                                                                'enum': ['pending',
                                                                                         'in_progress',
                                                                                         'completed']}}}}},
                   'required': ['content', 'status'],
                   'type': 'object'},
  'description': 'Create/Update task list.'}]
    return anthropic_style_tools

messages = test_messages()
anthropic_style_tools = test_antropic_style_tools()


stream = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system="You are a helpful assistant.",
            messages=messages,
            stream=True,
            tools=anthropic_style_tools,
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

print(f"\n\nFull Response:\n{full_response}")

