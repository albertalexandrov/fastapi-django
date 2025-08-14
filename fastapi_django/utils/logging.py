import logging
from logging.config import dictConfig

from fastapi_django.conf import settings


def configure_logging():
    if settings.LOGGING:
        logging.config.dictConfig(settings.LOGGING)
