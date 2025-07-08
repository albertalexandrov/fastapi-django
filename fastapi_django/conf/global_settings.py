API_TITLE = "API title not specified"
API_SUMMARY = "API summary not specified"
API_DESCRIPTION = "API description not specified"
API_DOCS_ENABLED = False
API_VERSION = "API version not specified"
API_DEBUG = False
API_PREFIX = ""

MIDDLEWARES = ["default.middleware.example.Middleware"]

PROMETHEUS_ENABLED = False
PROMETHEUS_SHOULD_GZIP = True
PROMETHEUS_NAME = "prometheus_metrics"

TRUSTED_HOST_MIDDLEWARE_ALLOWED_HOSTS = ["*"]

# DATABASES = {}

# UVICORN_APP определяется непосредственно в настройках приложения,
# тк библиотека предоставляет только функцию get_default_app, которая создает экзмепляр приложения
UVICORN_WORKERS = 1
UVICORN_HOST = "localhost"
UVICORN_PORT = 8000
UVICORN_RELOAD = True
