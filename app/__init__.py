import datetime
import enum
import logging
import pathlib
import typing


class Logger:
    LOG_DIR: typing.Final[pathlib.Path] = pathlib.Path("logs")

    class LogLevel(enum.Enum):
        CRITICAL = logging.CRITICAL
        DEBUG = logging.DEBUG
        ERROR = logging.ERROR
        FATAL = logging.FATAL
        INFO = logging.INFO
        WARNING = logging.WARNING

    def __init__(
        self,
        name: str,
        log_level: LogLevel = LogLevel.DEBUG,
        initial_indent_level: int = 0,
    ) -> None:
        self.formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d %(levelname)8s | %(message)s ",
            datefmt="%H:%M:%S",
        )

        self.initial_indent_level = initial_indent_level
        self.log_file = self._get_log_file_path()
        self.log_level = log_level.value

        self.file_handler = logging.FileHandler(self.log_file)
        self.file_handler.setFormatter(self.formatter)
        self.file_handler.setLevel(self.log_level)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(self.log_level)

    def _get_indent_space(self, indent_level: int | None) -> str:
        return "  " * (self.initial_indent_level + (indent_level or 0))

    def _get_log_file_path(self) -> pathlib.Path:
        log_file_name = datetime.date.today().isoformat() + ".log"
        log_file = self.LOG_DIR.joinpath(log_file_name)

        return log_file

    def critical(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.critical(indent_space + msg, *args)

    def debug(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.debug(indent_space + msg, *args)

    def error(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.error(indent_space + msg, *args)

    def fatal(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.fatal(indent_space + msg, *args)

    def info(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.info(indent_space + msg, *args)

    def warning(
        self,
        msg: str,
        *args: object,
        indent_level: int | None = None,
    ) -> None:
        indent_space = self._get_indent_space(indent_level)
        self.logger.warning(indent_space + msg, *args)
