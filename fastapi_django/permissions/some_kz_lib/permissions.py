"""
request.user имеет структуру данных (но в модели Pydantic):

{
    'id': 1,
    'username': 'username@cobmk.com',
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'middle_name': '',
    'groups': [{
        'id': 1,
        'name': 'group1',
        'permissions': [{
            'id': 1,
            'name': "Permission 1",
            'codename': 'perm1'
        }, {
            'id': 2,
            'name': "Permission 2",
            'codename': 'perm2'
        }]
    }, {
        'id': 2,
        'name': 'group2',
        'permissions': [{
            'id': 3,
            'name': "Permission 3",
            'codename': 'perm3'
        },
        ]
    }],
    'partner': {
        'id': 1,
        'name': 'КА',
        'sap_code': '01010101010'
    },
    'is_staff': False,
    'is_active': True,
    'is_superuser': False
}
"""

from starlette.requests import Request

from fastapi_django.permissions import BasePermission


class CodenamePermission(BasePermission):  # TODO: название не очень, но ничего другого придумать не смог
    def __init__(self, codename: str):
        self._codename = codename

    async def __call__(self, request: Request) -> bool:
        return self._has_user_in_scope(request) and self._codename in request.user.permissions


class RolePermission(BasePermission):
    def __init__(self, role_name: str):
        self._role_name = role_name

    async def __call__(self, request: Request) -> bool:
        return self._has_user_in_scope(request) and self._role_name in request.user.roles
