import logging
import os
from datetime import datetime
from pathlib import Path

from hai.version import __appname__

# =====================================================================
# 拦截 LogRecord 创建过程，自动注入 request_id
# =====================================================================
old_factory = logging.getLogRecordFactory()


def worker_context_record_factory(*args, **kwargs):
    from hepai.tools.request_context import request_id_context
    record = old_factory(*args, **kwargs)
    # 获取当前协程/上下文的 request_id
    record.request_id = request_id_context.get()
    return record


logging.setLogRecordFactory(worker_context_record_factory)


class Logger:
    LOGGING_LEVEL_NAME = os.environ.get('LOGGING_LEVEL_NAME', "INFO")
    LOGGING_LEVEL = logging.getLevelName(LOGGING_LEVEL_NAME)

    format_str = f"\033[1;35m[%(asctime)s]\033[0m \033[1;32m[%(name)s]\033[0m " \
                 f"\033[1;33m[%(request_id)s]\033[0m " \
                 f"\033[1;36m[%(levelname)s]:\033[0m %(message)s"

    logg_dir = f'{Path.home()}/.{__appname__}_logs'

    @classmethod
    def get_logger(cls, name=None, **kwargs):
        return cls.getLogger(name, **kwargs)

    @classmethod
    def getLogger(cls, name=None, **kwargs):
        name = name if name else 'root'
        name_length = kwargs.get('name_length', 12)
        name = f'{name:<{name_length}}'
        level = kwargs.get('level', cls.LOGGING_LEVEL)

        logging.basicConfig(level=level,
                            format=cls.format_str,
                            force=True)

        logger = logging.getLogger(name)

        if not os.path.exists(cls.logg_dir):
            os.makedirs(cls.logg_dir, exist_ok=True)

        # 使用 datetime 获取当前时间
        current_time = datetime.now().strftime('%Y%m%d_%H%M')

        fh = logging.FileHandler(f'{cls.logg_dir}/{current_time}.log')
        fh.setLevel(level=level)
        fh.setFormatter(logging.Formatter(cls.format_str))

        # 避免多次调用 getLogger 导致同一个日志被打印多遍
        if not logger.handlers:
            logger.addHandler(fh)

        return logger


if __name__ == "__main__":
    import uuid
    from hepai.tools.request_context import request_id_context

    log = Logger.get_logger("MainModule")

    # 场景 1：未处于请求上下文中（例如 Worker 刚启动时的初始化日志）
    log.info("这是一个普通信息，没有设置 ID，默认显示为 system")

    # 场景 2：模拟 FastAPI 中间件拦截到了一个请求并设置上下文
    req_id = f"wk-req-{uuid.uuid4().hex[:8]}"
    token = request_id_context.set(req_id)

    try:
        log.warning("进入了请求上下文，现在日志会自动带上生成的 req_id 了")

        db_log = Logger.get_logger("Database", level=logging.DEBUG, name_length=20)
        db_log.debug("正在连接数据库...")
        db_log.info("数据库连接成功")
    finally:
        # 场景 3：请求结束，中间件清理上下文
        request_id_context.reset(token)

    log.error("离开了请求上下文，ID 又自动恢复回默认的 system 了")

    print(f"\n日志文件已保存至: {Logger.logg_dir}")
