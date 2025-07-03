"""Modulo para controlar globalmente los logs."""

from logging import StreamHandler, Formatter, Filter, basicConfig, DEBUG, CRITICAL, getLogger

LOGGING_DATE_FMT = "%Y-%m-%d %H:%M:%S %z"
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(context)s] %(message)s"
LOGGING_HANDLER = StreamHandler()
LOGGING_FORMATTER = Formatter(LOGGING_FORMAT, datefmt=LOGGING_DATE_FMT)
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)

class LoggingFilterContext(Filter):
    """Verifica que en el formato del logging exista el parametro `context`"""

    def filter(self, record):
        if not hasattr(record, "context"):
            record.context = record.module
        return True

LOGGING_HANDLER.addFilter(LoggingFilterContext())
basicConfig(handlers=[LOGGING_HANDLER], level=DEBUG)

# Silenciar los loggers de las dependencias
SILENT = CRITICAL + 1

getLogger("asyncio").setLevel(SILENT)
getLogger("hypercorn.error").setLevel(SILENT)
getLogger("hypercorn.access").setLevel(SILENT)
getLogger("apscheduler.scheduler").setLevel(SILENT)
