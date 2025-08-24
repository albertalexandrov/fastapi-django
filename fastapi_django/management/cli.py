import uvicorn
from IPython import embed
from typer import Typer

from fastapi_django.conf import settings
from fastapi_django.exceptions import ImproperlyConfigured

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
        if (param := param.lower()) == "log_config":
            raise ImproperlyConfigured("Настройки логирования необходимо определять в настройке LOGGING")
        params[param] = getattr(settings, setting)
    uvicorn.run(**params, log_config=settings.LOGGING)


@typer.command()
def echo(message: str):
    """
    Эхо-команда
    """
    print(f"Echo: {message}")


@typer.command()
def shell() -> None:
    """
    Runs a Python interactive interpreter (iPython)
    """
    embed()
