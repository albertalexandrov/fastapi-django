import uvicorn
from typer import Typer

from fastapi_django.conf import settings

typer = Typer(rich_markup_mode="markdown")


@typer.command()  # TODO: можно определить rich_help_panel, которые действуют объединяюще как теги в сваггере
def runserver():
    """
    Запускает приложение при помощи Uvicorn.

    Параметры запуска Uvicorn задаются в settings. Названия параметров должны иметь префикс UVICORN_
    Далее идут названия параметров функции uvicorn.run в верхнем регистре. Таким образом, параметр,
    соответствующий параметру workers будет иметь название UVICORN_WORKERS, для port - UVICORN_PORT и тд
    """
    params = {}
    uvicorn_settings = [setting for setting in dir(settings) if setting.startswith("UVICORN_")]
    for setting in uvicorn_settings:
        _, param = setting.split("_", 1)
        params[param.lower()] = getattr(settings, setting)
    uvicorn.run(**params)


@typer.command()
def echo(message: str):
    """
    Эхо-команда
    """
    print(f"Echo: {message}")
