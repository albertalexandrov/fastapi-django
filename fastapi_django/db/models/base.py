from typing import Self, Any
from uuid import uuid4, UUID

from sqlalchemy import MetaData, BigInteger, SmallInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata = MetaData()


class Model(AsyncAttrs, DeclarativeBase):
    metadata = metadata

    def update(self, **values: Any) -> Self:
        for key, value in values.items():
            setattr(self, key, value)
        return self


class UUIDv4Base(Model):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)


class IntBase(Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class BigIntBase(Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)


class SmallIntBase(Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
