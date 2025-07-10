from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from fastapi_django.db import engine

# session_factory выступает как единственный способ создания сессий (при тестировании пригодится)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
session_context_var: ContextVar[Any] = ContextVar("sqlalchemy_session", default=None)


@asynccontextmanager
async def contextified_transactional_session(**kw: Any):
    """
    Управляет жизненным циклом сессии, присоединенной к внешней транзакции

    Внешняя транзакция необходима для того, чтобы не зависет от возможных коммитов сессии

    Помещенная в ContextVar сессия доступна потом в репозиториях

    можно использовать в произвольных местах, а не только в контексте http запросов, напр., в асинхронных задачах:
        async with transactional_in_context_session() as session:
            stmt = select(MyModel)
            ....
    """
    assert session_context_var.get() is None, "Сессия была создана ранее"  # TODO: точно нужно запрещать повторное использование?
    connection = await engine.connect()
    transaction = await connection.begin()
    session = session_factory(bind=connection, **kw)
    token = session_context_var.set(session)
    try:
        yield session
        await transaction.commit()
    except Exception as e:
        await transaction.rollback()
        raise e
    finally:
        await session.close()
        await connection.close()
        session_context_var.reset(token)


@asynccontextmanager
async def contextified_autocommit_session(**kw: Any):
    """
    Управляет жизненным циклом сессии с уровнем изоляции AUTOCOMMIT

    AUTOCOMMIT может быть полезен как микрооптимизация (не генерить транзакций без необходимости - селекты)

    Помещенная в ContextVar сессия доступна потом в репозиториях

    можно использовать в произвольных местах, а не только в контексте http запросов, напр., в асинхронных задачах:
        async with transactional_in_context_session() as session:
            stmt = select(MyModel)
            ....
    """
    assert session_context_var.get() is None, "Сессия была создана ранее"  # TODO: точно нужно запрещать повторное использование?
    autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
    session = session_factory(bind=autocommit_engine, **kw)
    token = session_context_var.set(session)
    yield session
    await session.close()
    session_context_var.reset(token)
