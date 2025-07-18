from starlette.requests import Request

from fastapi_django.permissions.base import BasePermission

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAuthenticated(BasePermission):
    async def _has_permission(self, request: Request) -> bool:
        return self._has_user_in_scope(request)


class AllowAny(BasePermission):
    async def _has_permission(self, request: Request) -> bool:
        return True


class IsAuthenticatedOrReadOnly(BasePermission):
    async def _has_permission(self, request: Request) -> bool:
        return request.method in SAFE_METHODS or self._has_user_in_scope(request)


class ForFailPermission(BasePermission):
    async def _has_permission(self, request: Request) -> bool:
        return False


class PermissionClasses:
    def __init__(self, *permissions):
        if not permissions:
            raise ValueError("Пермишены не переденаны")
        self._permissions = permissions

    async def __call__(self, request: Request) -> None:
        for permission in self._permissions:
            await permission(request=request)
