openai_style_tools = [
{'type': 'function',
  'function': {'name': 'pdf_manual_search',
               'description': '\n'
                              '    该函数通过匹配输入问题相近的文档目录及其对应的文件markdown文件位置，帮助进行下一步文档的仔细阅读\n'
                              '    Arguments:\n'
                              '        question: The question to search for.\n'
                              '        max_items: The maximum number of items to return.\n'
                              '        similarity_threshold: The similarity threshold for '
                              'filtering results.\n'
                              '    ',
               'parameters': {'type': 'object',
                              'properties': {'question': {'description': 'question',
                                                          'title': 'Question',
                                                          'type': 'string'},
                                             'max_items': {'default': 5,
                                                           'description': 'max_items',
                                                           'title': 'Max Items',
                                                           'type': 'integer'},
                                             'similarity_threshold': {'default': 0.2,
                                                                      'description': 'similarity_threshold',
                                                                      'title': 'Similarity '
                                                                               'Threshold',
                                                                      'type': 'number'}},
                              'required': ['question'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'run_bash',
               'description': 'Execute shell command in workspace directory.\n'
                              '\n'
                              '        The working directory persists across calls: cd commands '
                              'take effect\n'
                              '        for subsequent invocations, as long as the target stays '
                              'within the\n'
                              '        allowed workspace.\n'
                              '        ',
               'parameters': {'type': 'object',
                              'properties': {'cmd': {'description': 'cmd',
                                                     'title': 'Cmd',
                                                     'type': 'string'}},
                              'required': ['cmd'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'run_read',
               'description': '\n'
                              '        Read file contents.\n'
                              '        \n'
                              '        Args:\n'
                              '            path : Path to file.\n'
                              '            minilimit : The start of  Maximum number of lines to '
                              'read.\n'
                              '            maxlimit : The end of  Maximum number of lines to '
                              'read.\n'
                              '        ',
               'parameters': {'type': 'object',
                              'properties': {'path': {'description': 'path',
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
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'run_write',
               'description': 'Write content to file.',
               'parameters': {'type': 'object',
                              'properties': {'path': {'description': 'path',
                                                      'title': 'Path',
                                                      'type': 'string'},
                                             'content': {'description': 'content',
                                                         'title': 'Content',
                                                         'type': 'string'}},
                              'required': ['path', 'content'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'run_edit',
               'description': 'Replace exact text in file.',
               'parameters': {'type': 'object',
                              'properties': {'path': {'description': 'path',
                                                      'title': 'Path',
                                                      'type': 'string'},
                                             'old_text': {'description': 'old_text',
                                                          'title': 'Old Text',
                                                          'type': 'string'},
                                             'new_text': {'description': 'new_text',
                                                          'title': 'New Text',
                                                          'type': 'string'}},
                              'required': ['path', 'old_text', 'new_text'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'retreve_from_memory',
               'description': 'Retrieve relevant information from memory. No special requirements, '
                              'just input the question.\n'
                              '        \n'
                              '        Arguments:\n'
                              '            question: The question to retrieve relevant '
                              'information.\n'
                              '            document_ids: The document_ids to retrieve relevant '
                              'information. Default is [].\n'
                              '            page_size: The number of chunks to retrieve. Default is '
                              '10.\n'
                              '            similarity_threshold: The similarity threshold. Default '
                              'is 0.2.\n'
                              '            vector_similarity_weight: The vector similarity weight. '
                              'Default is 0.3.\n'
                              '            top_k: The top_k. Default is 1024.\n'
                              '            rerank_id: The rerank_id. Default is '
                              '"hepai/bge-reranker-v2-m3___OpenAI-API@OpenAI-API-Compatible".\n'
                              '            keyword: Whether to use keyword. Default is True.\n'
                              '            cross_languages: The cross_languages. Default is '
                              '["English", "Chinese"].\n'
                              '        \n'
                              '        Return:\n'
                              '                The string of relevant information.\n'
                              '        ',
               'parameters': {'type': 'object',
                              'properties': {'question': {'description': 'question',
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
                                                                      'title': 'Similarity '
                                                                               'Threshold',
                                                                      'type': 'number'},
                                             'vector_similarity_weight': {'default': 0.3,
                                                                          'description': 'vector_similarity_weight',
                                                                          'title': 'Vector '
                                                                                   'Similarity '
                                                                                   'Weight',
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
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'summry_conversation_to_memory',
               'description': "Summarize the conversation by user's prompt.\n"
                              '        \n'
                              '        Arguments:\n'
                              "            summary_task_prompt: The user's request for summarizing "
                              'the conversation.\n'
                              '        \n'
                              '        Note:\n'
                              '            If the specific summarizing request is not provided , '
                              'the default prompt will be used.\n'
                              '        ',
               'parameters': {'type': 'object',
                              'properties': {'summary_task_prompt': {'anyOf': [{'type': 'string'},
                                                                               {'type': 'null'}],
                                                                     'default': None,
                                                                     'description': 'summary_task_prompt',
                                                                     'title': 'Summary Task '
                                                                              'Prompt'}},
                              'required': [],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'UpdateUserConfig',
               'description': 'Update user profile configuration including name, and assistant '
                              'settings.\n'
                              '\n'
                              'Use this tool when the user wants to:\n'
                              '- Change their name or how they want to be addressed\n'
                              "- Update the assistant's name\n"
                              '- Configure whether to ask before planning tasks\n'
                              '\n'
                              'You can update one or multiple fields at once. Only provide the '
                              'fields that need to be updated.',
               'parameters': {'type': 'object',
                              'properties': {'user_name': {'type': 'string',
                                                           'description': "User's name for "
                                                                          'personalized '
                                                                          'addressing'},
                                             'agent_name': {'type': 'string',
                                                            'description': "Assistant's name as "
                                                                           'preferred by the user'},
                                             'ask_before_plan': {'type': 'boolean',
                                                                 'description': 'Whether to show '
                                                                                'the plan and ask '
                                                                                'for user approval '
                                                                                'before executing '
                                                                                'complex tasks'}},
                              'required': [],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'Skill',
               'description': 'Load a skill to gain specialized knowledge for a task.\n'
                              '\n'
                              'Available skills:\n'
                              '- ragflow_knowledge: '
                              '指导用户如何处理PDF格式的文献、使用RAGFlow矢量知识库框架进行个人的文献管理。当用户提到如何使用RAGFlow、如何上传PDF到RAGFlow知识库、如何处理长文档进行混合检索时立即使用此技能。\n'
                              '- research-paper-writer: Creates formal academic research papers '
                              'following IEEE/ACM formatting standards with proper structure, '
                              'citations, and scholarly writing style. Use when the user asks to '
                              'write a research paper, academic paper, or conference paper on any '
                              'topic.\n'
                              '- skill-creator: Create new skills, modify and improve existing '
                              'skills, and measure skill performance. Use when users want to '
                              'create a skill from scratch, edit, or optimize an existing skill, '
                              'run evals to test a skill, benchmark skill performance with '
                              "variance analysis, or optimize a skill's description for better "
                              'triggering accuracy.\n'
                              '- user_system_config: '
                              '修改和更新用户的个人画像、系统提示词、工具偏好配置等。在用户需要调整自己的昵称、智能助手的回复性格、工作流程等系统提示词、工具使用偏好等情况时使用。\n'
                              '- academic-writing: You are an academic writing expert specializing '
                              'in scholarly papers, literature reviews, research methodology, and '
                              'thesis writing. You must adhere to strict academic standards in all '
                              'outputs.## Core Requirements1. **Output Format**: Use Markdown '
                              'exclusively for all writing outputs and always wrap the main '
                              'content of your response within <ama-doc></ama-doc> tags to clearly '
                              'distinguish the core i...\n'
                              '- update_tools: 指导如何更新智能助手的mcp、函数工具列表。\n'
                              '- academic-writing-refiner: Refine academic writing for computer '
                              'science research papers targeting top-tier venues (NeurIPS, ICLR, '
                              'ICML, AAAI, IJCAI, ACL, EMNLP, NAACL, CVPR, WWW, KDD, SIGIR, CIKM, '
                              'and similar). Use this skill whenever a user asks to improve, '
                              'polish, refine, edit, or proofread academic or research writing — '
                              'including paper drafts, abstracts, introductions, related work '
                              'sections, methodology descriptions, experiment write-ups, or '
                              'conclusion sections. Also trigger when users paste LaTeX content '
                              'and ask for writing help, mention "camera-ready", "rebuttal", '
                              '"paper revision", or reference any academic venue or conference. '
                              'This skill handles both full paper refinement and '
                              'section-by-section editing.\n'
                              '- pdf_manual_search: 基于pdf_manual_search工具的手册检索教程，可以查询《spec - X-Ray '
                              'Diffraction Software》，OpenDrSai智能体开发等手册内容。\n'
                              '- download_github_skills: '
                              '指导智能体如何从给定的github仓库路径中下载指定的skill文件夹安装到用户的skills目录中。\n'
                              '- update_subagent: 指导如何更新智能助手的子智能体(subagent)的列表。\n'
                              '\n'
                              'When to use:\n'
                              '- IMMEDIATELY when user task matches a skill description\n'
                              '- Before attempting domain-specific work (PDF, MCP, etc.)\n'
                              '\n'
                              'The skill content will be injected into the conversation, giving '
                              'you\n'
                              'detailed instructions and access to resources.',
               'parameters': {'type': 'object',
                              'properties': {'skill': {'type': 'string',
                                                       'description': 'Name of the skill to load'}},
                              'required': ['skill'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'Task',
               'description': 'Spawn a subagent for a focused subtask.\n'
                              '\n'
                              'Agent types:\n'
                              '- explore: Read-only agent for exploring code, finding files, '
                              'searching\n'
                              '- coder: Full agent for writing codes, implementing features and '
                              'fixing bugs\n'
                              '- coder_executor: A computer terminal that performs no other action '
                              'than running Python scripts (provided to it quoted in ```python '
                              'code blocks), or sh shell scripts (provided to it quoted in ```sh '
                              'code blocks).\n'
                              '- plan: Planning agent for designing implementation strategies',
               'parameters': {'type': 'object',
                              'properties': {'description': {'type': 'string',
                                                             'description': 'Short task '
                                                                            'description (3-5 '
                                                                            'words)'},
                                             'prompt': {'type': 'string',
                                                        'description': 'The specific tasks that '
                                                                       'need to be executed by the '
                                                                       'sub agent. If the tasks '
                                                                       'include code blocks, '
                                                                       'files, etc. that need to '
                                                                       'be executed, they must be '
                                                                       'filled in completely.'},
                                             'agent_type': {'type': 'string',
                                                            'enum': ['explore',
                                                                     'coder',
                                                                     'coder_executor',
                                                                     'plan']}},
                              'required': ['description', 'prompt', 'agent_type'],
                              'additionalProperties': False},
               'strict': False}},
 {'type': 'function',
  'function': {'name': 'TodoWrite',
               'description': 'Create/Update task list.',
               'parameters': {'type': 'object',
                              'properties': {'items': {'type': 'array',
                                                       'items': {'type': 'object',
                                                                 'properties': {'content': {'type': 'string'},
                                                                                'status': {'type': 'string',
                                                                                           'enum': ['pending',
                                                                                                    'in_progress',
                                                                                                    'completed']}}}}},
                              'required': ['content', 'status'],
                              'additionalProperties': False},
               'strict': False}}]


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
