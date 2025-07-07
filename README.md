# Работа с базами данных

## Кейсы для множественных БД

В одну БД (мастер) пишется, в другую синхронизируется и из нее читается. 

## repository-sqlalchemy

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


