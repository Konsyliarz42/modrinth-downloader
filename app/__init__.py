import datetime
import enum
import logging
import pathlib
import typing

LOG_DIR: typing.Final[pathlib.Path] = pathlib.Path("logs")


class LogLevel(enum.Enum):
    CRITICAL = logging.CRITICAL
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    FATAL = logging.FATAL
    INFO = logging.INFO
    WARNING = logging.WARNING


def get_logger(name: str, level: LogLevel | None = None) -> logging.Logger:
    log_level = (level or LogLevel.DEBUG).value
    log_file_name = datetime.date.today().isoformat() + ".log"
    log_file = LOG_DIR.joinpath(log_file_name)

    formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)8s | %(message)s ", "%H:%M:%S")

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)

    return logger
