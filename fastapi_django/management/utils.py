from inspect import iscoroutinefunction
from typing import Any

from fastapi_django.management import cli
from fastapi_django.utils import coro


def register_command(command, **kw: Any) -> None:
    if iscoroutinefunction(command):
        command = coro(command)
    cli.command(**kw)(command)
