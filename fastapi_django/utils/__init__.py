import asyncio
from functools import wraps
from typing import Callable, Any


def coro(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))
    return wrapper
