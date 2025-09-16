**2025-04-09: **

- 1.更新适配了autogen 0.5.1版本，支持openai系列模型的Structured Outputs，deepseek系列目前没有该功能， 具体见案例```example/oai_client/assistant_structured_output.py```。

- 2.将后端持久化保持对象：thread、threadmanager传递到了自定义回复函数中，具体见案例```example/oai_client/assistant_custom_reply_demo_oai.py```。

- 3.修复了一些bug。

**2025-04-14: **

- 1.尝试修复了thread后端历史消息加载和前端历史消息加载可能的冲突的问题。具体而言，在```drsai/dr_sai.py```的```a_start_chat_completions```函数中，会通过对接前端```chat_id```创建或者检索后端的```thread```对象，并传递给后面的每一个智能体和groupchat，以保证前端和后端的智能体和多智能体之间的消息和设置都是一致的。```thread.messages```保存历史消息，并在每次智能体聊天中更新。由于前端每次都会传递当前聊天界面完整的消息记录，后端也会通过```threads_mgr.create_message```和自定义的逻辑保存消息记录。为了解决前端历史消息加载和后端历史消息加载可能存在的冲突的问题，新增```history_mode```参数，用于控制究竟是加载前端的历史消息还是后端的历史消息。前端的历史消息加载模式为```history_mode='frontend'```，后端的历史消息加载模式为```history_mode='backend'```。默认情况下，为后端的历史消息加载模式，即```history_mode='backend'```。这些加载的历史消息记录会被缓存到```thread.metadata["history_aoi_messages"]```中，在```drsai/modules/baseagent/drsaiagent.py```的```_call_llm```函数中被整合到上下文消息记录中。```history_mode```参数可以通过前端访问在```body```或者启动后端时在启动参数中传入。具体见案例```examples/oai_client/roundgroup_oai_thread.py、examples/oai_client/assistant_R1_oai.py```。

- 2.```thread.messages```的历史消息存储由```drsai/modules/baseagent/drsaiagent.py```的```_call_llm```函数转移到了```drsai/modules/baseagent/drsaiagent.py```的```a_start_chat_completions```函数中，通过捕捉```TextMessage```和```ToolCallSummaryMessage```事件来更新```thread.messages```。drsai智能体的内部的非思考文本输出和工具调用的输出会被捕捉并存储。用户还通过自定义事件和捕获来进行自定义储存修改。

- 3.自定义消息事件类型，使用多智能体系统时需要在```DrSaiGroupChat```中传入注册。具体见https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html。这意味着我们可以定义自己的消息类型，用户捕获特殊的事件进行操作。

**2025-04-15: **

- 1.open-webui重复打印：需要注释open-webui源码```utils/middleware.py```中的```post_response_handler```函数中的```tag_content_handler```函数中的：
```python
# if before_tag:
#     content_blocks[-1]["content"] = before_tag
```

- 2.已经修改了```drsai/backend/owebui_pipeline/pipelines/pipelines/drsai_pipeline.py```，默认将open-webui前端的```chat_id```作为后端的```thread_id```，这意味着前后端的状态可以通过```thread+chat_id```进行同步。同时thread已经被传递到了每个智能体、智能体的自定义回复函数和多智能体中，这意味每个智能体和用户的自定义开发都可与open-webui前端保持一致。注意：用户需要更新自己pipeline目录下的```drsai_pipeline.py```文件。

- 3.在autogen的代码，只存第一次"<think>"后的内容到```TextMessage```中，后面同一智能体多次内部"<think>"将不会被存入```TextMessage```中。请自定义回复函数开发者注意，这时候可以使用```history_mode='frontend'```来加载前端的历史消息，这个BUG后面将会被修复。

**2025-04-18: **

- 1.发现```drsai/backend/owebui_pipeline/pipelines/main.py```中的加载pipeline函数：load_module_from_path，在windos 11系统gbk编码下使用```with open(module_path, 'r') as file:```读取pipeline python文件时出现编码错误，改成了：```with open(module_path, 'r', encoding='utf-8') as file:```。

- 2.将``opendrsai``分为```main```和```stable```两个版本，在```main```开发测试完成后会发布稳定版到```stable```分支，所有的pipy安装包都将以```stable```分支发布，```requriements.txt```中将会固定所有环境，目前第一次稳定版本是```0.5.3```，但是未更正上一条BUG，将会在下次发布时修复。

**2025-05-04: **

- 1.```AssistantAgent```在不传入```model_client```时会默认实例化"openai/gpt-4o"。

- 2.在```AssistantAgent```的```reply_function```中，传入的tools类型改为Autogen-0.5.5版的新类型-Workbench：```tools: Union[StaticWorkbench, Workbench]```。Workbench可以将传入的函数和参数封装成一个对象，方便后续调用和执行，具体示例见```drsai/modules/baseagent/toolagent.py```和```examples/oai_client/assistantagent_tool_call_reply_oai.py```。

- 3.增加了```tools_reply_function```和```tools_recycle_reply_function```两个针对工具执行的自定义回复函数，具体见```drsai/modules/baseagent/toolagent.py```和```examples/oai_client/assistantagent_tool_call_reply_oai.py```：
**tools_reply_function**：在执行工具时，如果有返回值，则使用大模型对返回值进行整理成人类可读的文本，并返回给用户。
**tools_recycle_reply_function**：在执行任务需要多个工具时，先根据任务进行多工具使用规划，然后按照规划好的工具执行，并将执行结果整理成人类可读的文本，并返回给用户。

- 4.opendrsai支持了SWARM的多智能体系统与前端适配，能够无缝与前端对话。通过解析最后```TaskResult```中最后一条消息是否是```HandoffMessage```，且```target```是"user"，来通过thread保留上一轮对话的状态。注意：必须将AssissantAgent中的handoffs角色转移中的人类名称确定为"user"，才能被正确的启动上一轮对话。具体见```examples/oai_client/swarm_groupchat_oai.py```。