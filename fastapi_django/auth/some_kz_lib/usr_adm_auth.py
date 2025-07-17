from base64 import b64decode

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException
from fastapi.security.http import HTTPBearer
from httpx import HTTPStatusError
from jwt import PyJWTError
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

from fastapi_django.conf import settings
from fastapi_django.exceptions.http import HTTP401Exception


class Permission(BaseModel):
    id: int
    name: str
    codename: str


class RoleSerializer(BaseModel):
    id: int
    name: str
    permissions: list[Permission]


class Partner(BaseModel):
    id: int
    name: str
    sap_code: str


class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    middle_name: str
    groups: list[RoleSerializer]
    partner: Partner | None
    is_staff: bool | None
    is_active: bool | None
    is_superuser: bool | None

    @property
    def roles(self) -> set[str]:
        return {group.name for group in self.groups}

    @property
    def permissions(self) -> set[str]:
        result = set()
        for group in self.groups:
            for permission in group.permissions:
                result.add(permission.codename)
        return result


class UsrAdmAuth(HTTPBearer):
    """
    Аутентификация в сервисе User Administration

    Он не должен быть в этой библиотеке, но его можно вынести в какую нибудь специфичную для проекта библиотеку
    В КЗ эта библиотека - partners-utils

    Для работы классу необходимые (свои собственные) настройки:
    - USR_ADM_AUTH_HOST -хост сервиса User Administration
    - USR_ADM_AUTH_USERNAME - логин пользователя, от имени которого происходят запросы к сервису User Administration
    - USR_ADM_AUTH_PASSWORD - пароль пользователя, от имени которого происходят запросы к сервису User Administration
    - USR_ADM_AUTH_VERIFY - инструкция проверять или нет SSL-сертификаты
    - USR_ADM_AUTH_REALM_URL - урл Keycloak, по которому можно найти публичный ключ

    Не зря было отмечено, что у этого класс свои собственные настройки.  На мой взгляд это важно ради ясности и
    надежности (реализует SRP)

    """

    def __init__(
        self,
        *,
        bearerFormat: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True
    ):
        description = description or "Аутентификация в сервисе User Administration"
        super().__init__(
            bearerFormat=bearerFormat, scheme_name=scheme_name, description=description, auto_error=auto_error
        )

    async def __call__(self, request: Request) -> User | None:
        try:
            credentials = await super().__call__(request)
        except HTTPException:
            raise HTTP401Exception
        if credentials is None:
            if self.auto_error:
                raise HTTP401Exception
            return
        token = credentials.credentials
        try:
            header = jwt.get_unverified_header(token)
        except PyJWTError:
            if self.auto_error:
                raise HTTP401Exception
            return
        alg = header["alg"]
        public_key = await self._get_public_key()
        try:
            data = jwt.decode(
                token, key=public_key, algorithms=[alg], options=dict(verify_exp=True, verify_aud=False)
            )
        except PyJWTError:
            if self.auto_error:
                raise HTTP401Exception
            return
        try:
            user = await self._get_user(data["preferred_username"])
        except HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                # о том, что пользователя не существует, можно быть уверенным только если
                # от сервиса User Administration пришел ответ с кодом 404.  если же, получив
                # от сервиса, напр., код 500, и отдавая пользователю 401, можно легко быть
                # сбитым с толку при отладке ошибок
                if self.auto_error:
                    raise HTTP401Exception
                return
            raise e
        if not user.is_active:
            if self.auto_error:
                raise HTTP401Exception
            return
        request.scope["user"] = user
        return user

    async def _get_public_key(self) -> RSAPublicKey:
        # клиенты - самописные или готовые - для взаимодействия с Keycloak
        # не используются сознательно.  тут просто один запрос на незащищенную API
        client = httpx.AsyncClient(verify=settings.USR_ADM_AUTH_VERIFY)
        resp = await client.get(settings.USR_ADM_AUTH_REALM_URL)
        resp.raise_for_status()
        content = resp.json()
        key_data = b64decode(content["public_key"])
        return serialization.load_der_public_key(key_data)

    async def _get_user(self, username: str) -> User:
        # клиент не используется сознательно - тут всего один вызов API
        auth = httpx.BasicAuth(settings.USR_ADM_AUTH_USERNAME, settings.USR_ADM_AUTH_PASSWORD)
        client = httpx.AsyncClient(
            base_url=settings.USR_ADM_AUTH_HOST, auth=auth, verify=settings.USR_ADM_AUTH_VERIFY
        )
        resp = await client.get(f"api/users/{username}/")
        resp.raise_for_status()
        content = resp.json()
        return User(**content)
