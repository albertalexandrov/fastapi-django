"""
в fastapi отсутствует встроенное управление пользователями
в drf используется django-вая функция authenticate, которая ищет пользователя в предоставляемой django таблице

возможные кейсы аутентификации:

1. аутентификация в Кeycloak
2. аутентицикация в сервисе пользователей (напр., user administration)
3. аутентификация в собственной БД сервиса (напр., сервисный пользователь)
4. базовая аутентификация, но креды хранятся в настройках

"""

def auth():
    print("===> auth <===")


class BasicAuthentication:
    pass


async def authenticate_service_user(username: str, password: str):
    pass