from typer import Typer
from fastapi_django.conf import settings
from fastapi_django import setup
from uvicorn.importer import import_from_string

setup()
typer = Typer(rich_markup_mode="markdown")
management = [{"TYPER": "fastapi_django.management.cli:typer"}] + settings.MANAGEMENT

for item in management:
    typer.add_typer(import_from_string(item["TYPER"]), name=item.get("NAME"))

__all__ = ["typer"]
