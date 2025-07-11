from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from fastapi_django.db import engine

# session_factory выступает как единственный способ создания сессий (при тестировании пригодится)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
session_context_var: ContextVar[Any] = ContextVar("sqlalchemy_session", default=None)


async def get_session(autocommit: bool = False, **kw: Any):
    """Возвращает кортеж из трех объектов для работы сессии.

    :param autocommit: Признак "AUTOCOMMIT".
    :return: Возвращает кортеж.
    """
    if autocommit:
        connection = engine.execution_options(isolation_level="AUTOCOMMIT")
        transaction = None
    else:
        connection = await engine.connect()
        transaction = await connection.begin()

    session = session_factory(bind=connection, **kw)
    return connection, transaction, session


async def set_session(autocommit: bool = False, **kw: Any):
    """Метод устанавливает значения (соединение, транзакция, сессия) в контекст.

    :param autocommit: Признак "AUTOCOMMIT".
    :return: Возвращает кортеж.
    """
    connection, transaction, session = session_context_var.get()
    if session is None:
        connection, transaction, session = await get_session(autocommit=autocommit, kw=kw)
        token = session_context_var.set((connection, transaction, session))
    return connection, transaction, session, token


@asynccontextmanager
async def contextified_transactional_session(**kw: Any):
    """Управляет жизненным циклом сессии, присоединенной к внешней транзакции.

    Внешняя транзакция необходима для того, чтобы не зависет от возможных коммитов сессии

    Помещенная в ContextVar сессия доступна потом в репозиториях

    можно использовать в произвольных местах, а не только в контексте http запросов, напр., в асинхронных задачах:
        async with transactional_in_context_session() as session:
            stmt = select(MyModel)
            ....
    """
    connection, transaction, session, token = await set_session(kw=kw)
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
    """Управляет жизненным циклом сессии с уровнем изоляции AUTOCOMMIT.

    AUTOCOMMIT может быть полезен как микрооптимизация (не генерить транзакций без необходимости - селекты)

    Помещенная в ContextVar сессия доступна потом в репозиториях

    можно использовать в произвольных местах, а не только в контексте http запросов, напр., в асинхронных задачах:
        async with transactional_in_context_session() as session:
            stmt = select(MyModel)
            ....
    """
    _, _, session, token = await set_session(autocommit=True, kw=kw)
    yield session
    await session.close()
    session_context_var.reset(token)
