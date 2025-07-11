from collections.abc import AsyncIterator, Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_django.db.sessions import contextified_autocommit_session, contextified_transactional_session


def contextify_transactional_session(**kw: Any) -> Callable:
    async def wrapper() -> AsyncIterator[AsyncSession]:
        async with contextified_transactional_session(**kw) as session:
            yield session

    return wrapper


def contextify_autocommit_session(**kw: Any) -> Callable:
    async def wrapper() -> AsyncIterator[AsyncSession]:
        async with contextified_autocommit_session(**kw) as session:
            yield session

    return wrapper


ContextifiedTransactionalSession = Annotated[AsyncSession, Depends(contextify_transactional_session())]
ContextifiedAutocommitSession = Annotated[AsyncSession, Depends(contextify_autocommit_session())]
