from typing import Any

from fastapi import Query, Request
from pydantic import BaseModel, Field

from fastapi_django.db.repositories.queryset import QuerySet


class Ordering(BaseModel):
    ordering: list[str] = Field(Query(default_factory=list))  # TODO: а если нужно другое именование поля?

    def order_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.order_by(*self.ordering)


class Pagination(BaseModel):

    async def paginate_queryset(self, queryset: QuerySet) -> Any:
        raise NotImplementedError


class LimitOffsetPagination(Pagination):
    limit: int = Query(10, gt=0, le=100)
    offset: int = Query(0, ge=0)

    async def paginate_queryset(self, queryset: QuerySet) -> Any:
        # пример логики пагинации
        # пагинация знает, какие поля используются при пагинации
        count = await queryset.count()
        data = await queryset[self.offset:self.offset + self.limit]
        return {"count": count, "results": data}


class FilterSet(BaseModel):

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        conditions = self.model_dump(exclude_unset=True, exclude_none=True)
        return queryset.filter(**conditions)


class ListService:
    # базовый класс для сервиса, возвращающего список объектов
    # предоставляет возможности для фильтрации, пагинации, сортировки

    def __init__(self, request: Request | None = None, filterset=None, ordering=None, pagination=None):
        self._request = request
        self._filterset = filterset
        self._ordering = ordering
        self._pagination = pagination

    async def list(self, *args, **kwargs) -> Any:
        queryset = self.get_queryset()
        if self._filterset is not None:
            queryset = self._filterset.filter_queryset(queryset)
        if self._ordering is not None:
            queryset = self._ordering.order_queryset(queryset)
        if self._pagination:
            data = await self._pagination.paginate_queryset(queryset)
        else:
            data = await queryset
        return data

    def get_queryset(self, *args: Any, **kwargs: Any) -> QuerySet:
        raise NotImplementedError

    @classmethod
    def init(cls, *args: Any, **kw: Any) -> Any:
        # метод инициалиции сервиса.  для использования в Depends
        # предполагается, что каждый класс определяет, какие именно возможности будут использованы - фильтрация,
        # сортировка, пагинация.  например:
        # @classmethod
        # def init(
        #     cls,
        #     request: Request,
        #     filterset: UsersFilterSet = Depends(),
        #     ordering: UsersOrdering = Depends(),
        # ) -> Self:
        #     # метод, который использует fastapi для инициализации сервиса
        #     return cls(request=request, users=users, filterset=filterset, ordering=ordering, pagination=pagination)
        # из примера видно, что пагинация не была определена, сделаловательно, в качестве результата можно ожидать
        # НЕпагинированный список объекто
        return cls(*args, **kw)
