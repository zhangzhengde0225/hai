import logging
import os
from datetime import datetime
from pathlib import Path

__appname__ = "hepai"

current_factory = logging.getLogRecordFactory()
old_factory = getattr(current_factory, "_hepai_wrapped_factory", current_factory)


def worker_context_record_factory(*args, **kwargs):
    from hepai.tools.request_context import request_id_context

    record = old_factory(*args, **kwargs)
    record.request_id = request_id_context.get()
    return record


logging.setLogRecordFactory(worker_context_record_factory)
worker_context_record_factory._hepai_wrapped_factory = old_factory


class Logger:
    LOGGING_LEVEL_NAME = os.environ.get("LOGGING_LEVEL_NAME", "INFO")
    LOGGING_LEVEL = logging.getLevelName(LOGGING_LEVEL_NAME)

    format_str = (
        "\033[1;35m[%(asctime)s]\033[0m "
        "\033[1;32m[%(name)s]\033[0m "
        "\033[90m[%(request_id)s]\033[0m "
        "\033[1;36m[%(levelname)s]:\033[0m %(message)s"
    )

    logg_dir = os.environ.get("HEPAI_LOG_DIR", f"{Path.home()}/.{__appname__}_logs")

    @classmethod
    def get_logger(cls, name=None, **kwargs):
        return cls.getLogger(name, **kwargs)

    @classmethod
    def getLogger(cls, name=None, **kwargs):
        name = name if name else "root"
        name_length = kwargs.get("name_length", 12)
        name = f"{name:<{name_length}}"
        level = kwargs.get("level", cls.LOGGING_LEVEL)

        logging.basicConfig(level=level, format=cls.format_str, force=True)

        logger = logging.getLogger(name)
        if not logger.handlers:
            current_time = datetime.now().strftime("%Y%m%d_%H%M")
            try:
                os.makedirs(cls.logg_dir, exist_ok=True)
                fh = logging.FileHandler(f"{cls.logg_dir}/{current_time}.log")
                fh.setLevel(level=level)
                fh.setFormatter(logging.Formatter(cls.format_str))
                logger.addHandler(fh)
            except OSError as exc:
                logger.warning(
                    "File logging disabled, cannot write to %s: %s",
                    cls.logg_dir,
                    exc,
                )

        return logger
