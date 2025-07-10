from typing import Self

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

metadata = MetaData()


class Model(AsyncAttrs, DeclarativeBase):
    metadata = metadata

    def update(self, **values) -> Self:
        for key, value in values.items():
            setattr(self, key, value)
        return self
