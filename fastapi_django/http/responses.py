from typing import Generic, TypeVar

from pydantic import BaseModel

Item = TypeVar("Item")


class PaginatedResponse(BaseModel, Generic[Item]):
    count: int
    results: list[Item]
