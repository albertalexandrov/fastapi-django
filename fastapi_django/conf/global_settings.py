from typing import Any

UVICORN_APP = "web.app:create_app"
UVICORN_HOST = "localhost"
UVICORN_PORT = 8000
UVICORN_WORKERS = 1
UVICORN_FACTORY = True
UVICORN_RELOAD = True

API_PREFIX = ""

MIDDLEWARES = ["default.middleware.example.Middleware"]

PROMETHEUS_ENABLED = False

DATABASE: dict = {}
# пример:
# DATABASE: dict = {
#     "DRIVERNAME": "postgresql+asyncpg",
#     "USERNAME": "username",
#     "PASSWORD": "password",
#     "HOST": "localhost",
#     "PORT": 5432,
#     "DATABASE": "database",
#     "OPTIONS": {
#         "connect_args": {"timeout": 30},
#         "echo": True,
#         "pool_recycle": 3600,
#         # другие параметры, которые будут переданы как kw в функцию create_async_engine()
#     }
# }

MANAGEMENT: list[dict] = []

LOGGING: dict[str, Any] = {}

EMAIL_PROVIDERS: dict[str, Any] = {}

DEFAULT_CHARSET = "utf-8"

# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME = False

DEFAULT_EMAIL_PROVIDER_ALIAS = "default"

# рендеринг шаблонов

TEMPLATES_DIRECTORY = "templates"
TEMPLATES_ENV_OPTIONS: dict = {}
