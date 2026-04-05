from contextvars import ContextVar

# 仅仅定义这一个变量，绝对不引入任何其他模块
request_id_context: ContextVar[str] = ContextVar("request_id", default="system")