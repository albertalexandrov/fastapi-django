from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_django.conf import settings
from fastapi_django.exceptions import ImproperlyConfigured

# поддерживаемые диалекты SQLAlchemy https://docs.sqlalchemy.org/en/20/dialects/index.html
# SQLAlchemy как безоговорочный вариант для взаимодействия с БД

# TODO:
#  по умолчанию не устанавливать библиотеку SQLAlchemy
#  проверять факт установки SQLAlchemy


class EngineProxy:
    def __init__(self):
        if not settings.DATABASE:
            raise ImproperlyConfigured("База данных не сконфигурирована")
        # TODO: прочекать параметры для разных диалектов
        url = URL.create(
            drivername=settings.DATABASE["DRIVERNAME"],
            username=settings.DATABASE.get("USERNAME"),
            password=settings.DATABASE.get("PASSWORD"),
            host=settings.DATABASE.get("HOST"),
            port=settings.DATABASE.get("PORT"),
            database=settings.DATABASE["DATABASE"],
        )
        kw = settings.DATABASE.get("OPTIONS", {})
        self.__dict__["_engine"] = create_async_engine(
            url, **kw
        )  # иначе будет RecursionError: maximum recursion depth exceeded

    def __getattr__(self, item):
        return getattr(self._engine, item)

    def __setattr__(self, name, value):
        return setattr(self._engine, name, value)

    def __delattr__(self, name):
        return delattr(self._engine, name)


engine = EngineProxy()
