from inspect import Parameter, Signature
from typing import Any

from fastapi import HTTPException, Depends
from fastapi.requests import Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.base import SecurityBase
from typing_extensions import Annotated

from fastapi_django.exceptions.http import HTTP401Exception


def AuthenicationClasses(*authenticators):
    # позволяет определить несколько классов аутентификации.  классы должны быть наследниками SecurityBase или
    # наследниками его наследников, тк благодаря им в сваггере схемы аутентификации будут отображаться
    # также необходимо, чтобы классы не выбрасывали исключений, если им не удалось аутентифицировать запрос
    # вместо этого они должны возвращать None, как признак того, что аутентификация не удалась
    # это необходимо, тк один класс все же может аутентифицировать, но исключение в другом классе не даст этому
    # случиться, и это может ввести в заблуждение
    def wrapper(request: Request, **kwargs):
        print(request, kwargs)
        if not any(kwargs.values()):
            raise HTTP401Exception
    if not authenticators:
        raise ValueError("Не заданы классы аутентификации")
    for authenticator in authenticators:
        if not issubclass(authenticator.__class__, SecurityBase):
            raise ValueError(f"Класс аутентификации {authenticator.__class__.__name__} не является наследником {SecurityBase.__class__.__name__}")
        if authenticator.auto_error is True:
            raise ValueError(
                f"Значение {authenticator.__class__.__name__}.auto_error должно быть равно False, "
                f"чтобы отработали все аутентификации"
            )
    parameters = [
        Parameter("request", Parameter.POSITIONAL_OR_KEYWORD, annotation=Request),
    ]
    for idx, authenticator in enumerate(authenticators, 1):
        name = f"param{idx}"
        parameter = Parameter(
            name,
            Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[Any, Depends(authenticator)],
        )
        parameters.append(parameter)
    wrapper.__signature__ = Signature(parameters)
    return wrapper


class BasicAuthentication(HTTPBasic):
    # Базовый класс для базовой аутентификации

    async def __call__(self, request: Request) -> Any:  # type: ignore
        try:
            credentials = await super().__call__(request)
        except HTTPException:
            raise HTTP401Exception
        if user := await self._authenticate(credentials) is not None:
            request.scope["user"] = credentials
            return user
        if self.auto_error:
            raise HTTP401Exception
        return None

    async def _authenticate(self, credentials: HTTPBasicCredentials | None) -> Any:
        # это может быть например получение сервисного пользователя из бд с последующим
        # сравнением кредов с сохраненными.  метод при этом возвращает экземпляр пользователя
        raise NotImplementedError("Не реализована логика аутентификации")


class CredentialsBasicAuthentication(BasicAuthentication):
    # Базовая аутентификация, при которой происходит сравнение полученных кредов с заданными

    def __init__(self, username: str, password: str, *, scheme_name: str | None = None, realm: str | None = None, description: str | None = None, auto_error: bool = True):
        super().__init__(scheme_name=scheme_name, realm=realm, description=description, auto_error=auto_error)
        self._username = username
        self._password = password

    async def _authenticate(self, credentials: HTTPBasicCredentials | None) -> HTTPBasicCredentials | None:
        if credentials and self._username == credentials.username and self._password == credentials.password:
            return credentials
        return None
