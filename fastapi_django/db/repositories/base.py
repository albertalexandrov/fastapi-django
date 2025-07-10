import logging
from itertools import islice
from typing import Generic, Any, Type, Self

from fastapi_django.db.repositories.queryset import QuerySet
from fastapi_django.db.sessions import session_context_var
from fastapi_django.db.types import Model
from fastapi_django.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class BaseRepository(Generic[Model]):
    model_cls: Type[Model]

    def __init__(self):
        if not self.model_cls:
            raise ImproperlyConfigured(f"Не задана модель в атрибуте `{self.__class__.__name__}.model_cls`")
        self._session = session_context_var.get()
        assert self._session is not None, "Сессия не определена. Используйте декоратор"
        print(self._session)
        self._flush = False
        self._commit = False
        print(f"Инициировали репозиторий {self.__class__.__name__}")

    def _clone(self) -> Self:
        clone = self.__class__()
        clone._flush = self._flush
        clone._commit = self._commit
        return clone

    def flush(self, flush: bool = True, /) -> Self:
        clone = self._clone()
        clone._flush = flush
        return clone

    def commit(self, commit: bool = True, /) -> Self:
        clone = self._clone()
        clone._commit = commit
        return clone

    async def _flush_commit_reset(self, *objs: Model) -> None:
        if self._flush and not self._commit and objs:
            await self._session.flush(objs)
        elif self._commit:
            await self._session.commit()
        self._flush = False
        self._commit = False

    async def create(self, **kw: Any) -> Model:
        obj = self.model_cls(**kw)
        self._session.add(obj)
        await self._flush_commit_reset(obj)
        return obj

    async def bulk_create(self, values: list[dict], batch_size: int | None = None) -> list[Model]:
        if batch_size is not None and (not isinstance(batch_size, int) or batch_size <= 0):
            raise ValueError("batch_size должен быть целым положительным числом")
        objs = []
        if batch_size:
            it = iter(values)
            while batch := list(islice(it, batch_size)):
                batch_objs = [self.model_cls(**item) for item in batch]
                await self._flush_commit_reset(*batch_objs)
                objs.extend(batch_objs)
        else:
            for item in values:
                obj = self.model_cls(**item)
                objs.append(obj)
            await self._flush_commit_reset(*objs)
        return objs

    async def get_by_pk(self, pk: Any) -> Model | None:
        return await self._session.get(self.model_cls, pk)

    @property
    def objects(self) -> QuerySet:
        return QuerySet(self.model_cls, self._session)
