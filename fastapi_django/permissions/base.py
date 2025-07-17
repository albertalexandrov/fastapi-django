from starlette.requests import Request

from fastapi_django.exceptions.http import HTTP403Exception


class BasePermission:

    async def __call__(self, request: Request) -> bool:
        if await self._has_permission(request):
            return True
        raise HTTP403Exception

    async def _has_permission(self, request: Request) -> bool:
        raise NotImplementedError(f"Не реализована логика в методе {self.__class__.__name__}")

    def _has_user_in_scope(self, request: Request) -> bool:
        return "user" in request.scope
