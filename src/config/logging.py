import logging
import logging.config
import logging.handlers
from time import gmtime

from .settings import Settings


settings = Settings()


class LoggerConfigurator:
    _date_format: str = "%d/%m/%Y"
    _time_format: str = "%H:%M:%S"

    def __init__(self, level: str = settings.app.LOGGING_LEVEL):
        self._level: str = level
        logging.config.dictConfig(self.get_logger_configuration())

    def get_logger_configuration(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "ChatApp: {asctime} {levelname}: {message}",
                    "datefmt": f"{self._date_format} {self._time_format}",
                    "style": "{",
                },
            },
            "handlers": {
                "default": {
                    "()": logging.StreamHandler,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                    "level": self._level,
                },
                "logfile": {
                    "()": logging.handlers.TimedRotatingFileHandler,
                    "filename": settings.app.LOGFILE_PATH,
                    "level": self._level,
                    "formatter": "default",
                    "when": settings.app.LOGFILE_TTL_MEASURE.value,
                    "interval": settings.app.LOGFILE_TTL,
                    "encoding": "UTF-8",
                },
            },
            "loggers": {
                "chat_logger": {
                    "handlers": ["default", "logfile"],
                    "level": self._level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default", "logfile"],
                    "level": self._level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default", "logfile"],
                    "level": self._level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default", "logfile"],
                    "level": self._level,
                    "propagate": False,
                },
            },
        }

    @staticmethod
    def _make_utc_logger(logger: logging.Logger) -> logging.Logger:
        for handler in logger.handlers:
            handler.formatter.converter = gmtime
        return logger

    def get_logger(
        self, name: str = "chat_logger", utc: bool = False
    ) -> logging.Logger:
        """
        Поскольку логгеры в Python синглтоны, мы можем создавать сколько угодно
        инстансов этого объекта в любом модуле - это всегда один объект.
        """
        current_logger: logging.Logger = logging.getLogger(name)
        if utc:
            current_logger: logging.Logger = self._make_utc_logger(
                current_logger
            )
        return current_logger
