import logging
from contextlib import contextmanager
from contextvars import ContextVar
from logging.config import dictConfig
from typing import Any

from fastapi_django.conf import settings

# контекст логирования.  когда необходимо в контекст добавляются желаемые значения,
# которые затем будут доступны в LogRecord
logging_context_var = ContextVar("logging_context", default={})


def configure_logging():
    if settings.LOGGING:
        logging.config.dictConfig(settings.LOGGING)


@contextmanager
def logging_context(**kw: Any):
    # добавляет в контекст логирования желаемые значения
    current_context = logging_context_var.get()
    new_context = {**current_context, **kw}
    token = logging_context_var.set(new_context)
    try:
        yield
    finally:
        logging_context_var.reset(token)
