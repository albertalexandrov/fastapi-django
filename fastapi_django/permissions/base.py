from starlette.requests import Request


class BasePermission:

    async def __call__(self, request: Request) -> bool:
        raise NotImplementedError

    def _has_user_in_scope(self, request: Request) -> bool:
        return "user" in request.scope
