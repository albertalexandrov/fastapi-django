from collections.abc import Callable

from typer import Typer

from fastapi_django.management.commands.echo import echo
from fastapi_django.management.commands.runserver import runserver

cli = Typer()
commands: list[Callable] = [echo, runserver]

for command in commands:
    cli.command()(command)
