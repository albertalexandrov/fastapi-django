import logging
from contextlib import contextmanager
from contextvars import ContextVar
from logging.config import dictConfig
from typing import Any

from fastapi_django.conf import settings

# контекст логирования.  когда необходимо в контекст добавляются желаемые значения,
# которые затем будут доступны в LogRecord
_logging_context = ContextVar("log_context", default={})
default_record_factory = logging.getLogRecordFactory()


def log_record_factory(*args, **kwargs):
    # добавляет в LogRecord поля, которые пользователь положил в контекст логирования
    record = default_record_factory(*args, **kwargs)
    context = _logging_context.get({})
    record.__dict__.update(context)
    return record


def get_logging_config() -> dict:
    return settings.LOGGING() if callable(settings.LOGGING) else settings.LOGGING


def configure_logging():
    logging.setLogRecordFactory(log_record_factory)
    if settings.LOGGING:
        config = get_logging_config()
        logging.config.dictConfig(config)


@contextmanager
def logging_context(**kw: Any):
    # добавляет в контекст логирования желаемые значения
    current_context = _logging_context.get()
    new_context = {**current_context, **kw}
    token = _logging_context.set(new_context)
    try:
        yield
    finally:
        _logging_context.reset(token)


def update_logging_context(**kw: Any):
    # добавляет значение в контекст логирования, если тот существует
    try:
        current_context = _logging_context.get()
    except LookupError:
        return
    current_context.update(kw)
