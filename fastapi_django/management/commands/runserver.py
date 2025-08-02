import uvicorn

from fastapi_django.conf import settings


def runserver() -> None:
    """
    Запускает приложение при помощи Uvicorn.

    Параметры запуска Uvicorn задаются в settings.  Названия параметров должны иметь префикс UVICORN_
    Далее идут названия параметров функции uvicorn.run в верхнем регистре.  Таким образом, параметр,
    соответствующий параметру workers будет иметь название UVICORN_WORKERS, для port - UVICORN_PORT и тд
    """
    params = {}
    uvicorn_settings = [setting for setting in dir(settings) if setting.startswith("UVICORN_")]
    for setting in uvicorn_settings:
        _, param = setting.split("_", 1)
        params[param.lower()] = getattr(settings, setting)
    uvicorn.run(**params)
