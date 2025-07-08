# Работа с базами данных

## Названия библиотеки

fastapi-django - рабочее название (не финальное).

Варианты:

- fastango
- fastapix5
- fastapiq
- fastapic

## TODO

1. множественные БД (в одну БД (мастер) пишется, в другую синхронизируется и из нее читается.)
2. генерация шаблона проекта как в django (также генерируется файл manage.py, в котором дополняются переменные окружения 
и который является входной точкой в приложение)
2. прикинуть, какие еще консольные команды могут пригодиться (напр., миграции)
3. репозитории
4. http-исключения
5. разработать формат ошибок (ошибки для тоста, ошибки валидации)
5. интегрировать https://github.com/albertalexandrov/django-like-repositories
6. работа с БД не только в рамках апишки, но в рамках напр. асинхронных задач
7. расширяемые сервисы для наиболее частых операций типа получить по id, обновить, получить список и тд
8. инжектить сессию в мддлвари наверно не вариант, тк может быть несколько бд
9. закрепить терминологию контроллер/сервис/репозиторий?
10. троттлинг
11. настройки вьюх как в DRF
12. как переопределять дефолтные настройки вьюх? (напр по умолчанию ручки за авторизацией, но для одной какой то нужен доступ без аутентификации)
13. расширяемость либы как в django
14. пермишены

## Создание приложения

Библиотека предоставляет функцию `fastapi_django.app.get_default_app()`, которая создает экземпляр приложения FastAPI 
с параметрами, указанными в настройках в settings.py:

```python
from fastapi_django.app import get_default_app

# создается приложение с указанными или дефолтными настройками
app = get_default_app()
```

Далее происходит донастройка экземпляра приложения, напр., включение урлов приложения:

```python
app.include_router(test_router)
```

## Запуск приложения

Приложение запускается при помощи Uvicorn, который настраивается переменными окружения:

- UVICORN_APP
- UVICORN_WORKERS
- UVICORN_HOST
- UVICORN_PORT
- UVICORN_RELOAD

TODO: добавить другие настройки для функции uvicorn.run.

Определите настройки, указанные выше. В качестве UVICORN_APP пропишите путь до экземпляра приложения FastAPI, напр.:

```python
UVICORN_APP = "web.app:app"
```

Для запуска приложения используйте консольную команду `runserver`:

```shell
python manage.py runserver
```

Это запустит экземпляр указанного в UVICORN_APP приложения при помощи uvicorn. 

## Исследование имеющихся решений

[https://github.com/mjhea0/awesome-fastapi](https://github.com/mjhea0/awesome-fastapi)

### fastapi-sqla

Движки, сессии конфигурируются библиотекой. Параметры через энвы, для наименования которых необходимо придерживаться 
некоторых правил. 

Сессия создается в миддлварях и [записывается в fastapi.Request.state](https://github.com/dialoguemd/fastapi-sqla/blob/master/fastapi_sqla/async_sqla.py#L137). 
Затем эту сессию депенденси AsyncSessionDependency возвращает.

Сессия не хранится в contextvars.

Сессия конфигурируется по ключу и готова к использованию.

Пример использования в апишке:

```python
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_sqla import (
    AsyncSessionDependency,
    SessionDependency,
    SqlaAsyncSession,
    SqlaSession,
)

router = APIRouter()

# Preferred

ReadOnlySession = Annotated[SqlaSession, Depends(SessionDependency(key="read_only"))]
AsyncReadOnlySession = Annotated[SqlaAsyncSession, Depends(AsyncSessionDependency(key="read_only"))]


@router.get("/example")
def example(session: ReadOnlySession):
    return session.execute("SELECT now()").scalar()


@router.get("/async_example")
async def async_example(session: AsyncReadOnlySession):
    return await session.scalar("SELECT now()")
```

Использование вне контекста веб приложения:

```python
from fastapi import APIRouter, BackgroundTasks
from fastapi_sqla import open_async_session, open_session

router = APIRouter()


@router.get("/example")
def example(bg: BackgroundTasks):
    bg.add_task(run_bg)
    bg.add_task(run_async_bg)


def run_bg():
    with open_session() as session:
        session.execute("SELECT now()").scalar()
```

Идеи/мысли:

1. можно сделать в библиотеке депенденси DefaultSession, которая будет возвращать сессию из default движка


### repository-sqlalchemy

[https://github.com/ryan-zheng-teki/repository-sqlalchemy](https://github.com/ryan-zheng-teki/repository-sqlalchemy)

Сессия берется из контекста:

```python
session_context_var: ContextVar[any] = ContextVar("db_session", default=None)

class BaseRepository(Generic[ModelType], metaclass=SingletonRepositoryMetaclass):
    model = None

    @property
    def session(self) -> Session:
        return session_context_var.get()

    ...
```

Плюсы:

1. неявная инициализация сессии
2. есть транзакции

Минусы:

1. невозможно переопределить параметры создаваемой сессии
2. работает только с одной БД
3. неявная инициализация сессии

Мысли:

```python
_engine = None
_Session = None

def get_engine():
    global _engine
    if _engine is None:
        db_type = os.environ.get('DB_TYPE', 'postgresql')
        db_config = DatabaseConfig(db_type)
        _engine = DatabaseEngineFactory.create_engine(
            db_config)
    return _engine

def get_session():
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _Session()
```

добавить к методам выше параметр типа using, который указывает, какую БД использовать?

registry для engine-ов при множестве БД?

прямой доступ к (default) сессии?

как переопределить параметры сессии?

для кейсов множественных БД не подходит вариант с захардкоженной сессией, тк один и тот же репозиторий может
быть использован и для чтения и для записи. может оставить возможность автоматичского создания сессии для default и
добавить возможно задать сессию снаружи? или хотя бы указания using? или как using в Django в декораторе:

```python
def atomic(using=None, savepoint=True, durable=False):
    # Bare decorator: @atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return Atomic(DEFAULT_DB_ALIAS, savepoint, durable)(using)
    # Decorator: @atomic(...) or context manager: with atomic(...): ...
    else:
        return Atomic(using, savepoint, durable)
```

### FastAPI-SQLAlchemy
[https://pypi.org/project/FastAPI-SQLAlchemy](https://pypi.org/project/FastAPI-SQLAlchemy)

```python
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from app.models import User

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite://")

# once the middleware is applied, any route can then access the database session
# from the global ``db``

@app.get("/users")
def get_users():
    users = db.session.query(User).all()

    return users
```

Управление жизненным циклом сессии происходит в middleware.

Сессия хранится в contextvars.

Доступ к сессии через отдельный объект SQLAlchemy.

Нет транзакций.

Паттерн active record.

Не поддерживается.

