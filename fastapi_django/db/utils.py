from sqlalchemy import Column, ColumnCollection, inspect
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.util._collections import ReadOnlyProperties

from fastapi_django.db.exceptions import ColumnNotFoundError
from fastapi_django.db.types import Model


def validate_has_columns(model_cls: type[Model], *args: str) -> None:
    columns = inspect(model_cls).columns
    for col in args:
        if col not in columns:
            raise ColumnNotFoundError(model_cls, col)


def get_column(model_cls: type[Model], column_name: str) -> Column:
    column = inspect(model_cls).columns.get(column_name)
    if column is not None:
        return column
    raise ColumnNotFoundError(model_cls, column_name)


def get_columns(model_or_aliased_cls: type[Model] | AliasedClass) -> ColumnCollection:
    is_aliased = isinstance(model_or_aliased_cls, AliasedClass)
    model_cls = inspect(model_or_aliased_cls).mapper.class_ if is_aliased else model_or_aliased_cls
    return inspect(model_cls).columns


def get_pk(model_cls: type[Model]) -> Column:
    pk = inspect(model_cls).primary_key
    if len(pk) == 1:
        return pk[0]
    raise ValueError(
        f"Модель {model_cls.__name__} имеет составной первичный ключ. "
        "Работа с составными первичными ключами не предусмотрена"
    )


def get_model_cls(model_or_aliased_cls: type[Model] | AliasedClass) -> type[Model]:
    if isinstance(model_or_aliased_cls, AliasedClass):
        return inspect(model_or_aliased_cls).mapper.class_
    return model_or_aliased_cls


def get_relationships(model_or_aliased_cls: type[Model] | AliasedClass) -> ReadOnlyProperties:
    model_cls = get_model_cls(model_or_aliased_cls)
    return inspect(model_cls).relationships


def get_annotations(model_or_aliased_cls: type[Model] | AliasedClass) -> dict:
    model_cls = get_model_cls(model_or_aliased_cls)
    return model_cls.__dict__["__annotations__"]
