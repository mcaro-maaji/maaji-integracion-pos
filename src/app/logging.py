"""Modulo para controlar globalmente los logs."""

from logging import Formatter, StreamHandler, Filter, basicConfig, DEBUG, CRITICAL, getLogger

LOGGING_DATE_FMT = "%Y-%m-%d %H:%M:%S %z"
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(context)s] %(message)s"
LOGGING_FORMATTER = Formatter(LOGGING_FORMAT, datefmt=LOGGING_DATE_FMT)

class NoTracebackStreamHandler(StreamHandler):
    """Manejador para ignorar el parametro exc_info"""

    def format(self, record):
        record.exc_info = False
        return super().format(record)

class LoggingFilterContext(Filter):
    """Verifica que en el formato del logging exista el parametro `context`"""

    def filter(self, record):
        if not hasattr(record, "context"):
            record.context = record.module
        return True

class ContextLogger:
    """Wrapper que agrega `context` automatico"""
    def __init__(self, logger, context):
        self._logger = logger
        self._context = context

    def __getattr__(self, attr):
        log_method = getattr(self._logger, attr)
        if callable(log_method):
            def wrapper(*args, **kwargs):
                if "extra" not in kwargs:
                    kwargs["extra"] = {}
                kwargs["extra"].setdefault("context", self._context)
                return log_method(*args, **kwargs)
            return wrapper
        return log_method

LOGGING_FILTER_CONTEXT = LoggingFilterContext()
LOGGING_NO_TRACEBACK_HANDLER = NoTracebackStreamHandler()
LOGGING_NO_TRACEBACK_HANDLER.setFormatter(LOGGING_FORMATTER)
LOGGING_NO_TRACEBACK_HANDLER.addFilter(LOGGING_FILTER_CONTEXT)

basicConfig(level=DEBUG, handlers=[
    LOGGING_NO_TRACEBACK_HANDLER
])

def get_logger(name: str | None = None, context: str = None):
    """Devolver un logger con el nombre especificado."""
    logger = getLogger(name)
    if context:
        return ContextLogger(logger, context)
    return logger

# Silenciar los loggers de las dependencias
SILENT = CRITICAL + 1

LIST_LOGGER_SET_SILENT = [
    "asyncio",
    "hypercorn.error",
    "hypercorn.access",
    "apscheduler.scheduler",
    "apscheduler.executors",
    "apscheduler.executors.default",
    "urllib3.connectionpool",
    "tzlocal"
]

for name_logger in LIST_LOGGER_SET_SILENT:
    getLogger(name_logger).setLevel(SILENT)
