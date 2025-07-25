import sys

import uvicorn

from fastapi_django.conf import settings


def cli(argv=None) -> None:
    argv = argv or sys.argv[:]
    argv = argv[1:]
    command = argv[0]
    if command == "runserver":
        # если запускать командой fastapi-django runserver, то будет ошибка при чтении settings,
        # тк в PATH не будет пути до проекта, но если через manage.py, то путь будет добавлен
        # TODO: рассмотреть возможность других команд
        uvicorn.run(
            settings.UVICORN_APP,
            workers=settings.UVICORN_WORKERS,
            host=settings.UVICORN_HOST,
            port=settings.UVICORN_PORT,
            reload=settings.UVICORN_RELOAD,
        )
    elif command == "makemigrations":
        # TODO:
        #  предусмотреть возможность ручного использования alembic на случай,
        #  если не хватает возможностей, предоставляемых библиотекой
        pass
    else:
        print("Вас приветствует fastapi_django!")
