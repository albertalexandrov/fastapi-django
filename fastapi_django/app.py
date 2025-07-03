from functools import partial
from pathlib import Path

from fastapi import APIRouter, FastAPI
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from starlette.staticfiles import StaticFiles

from .conf import settings
from .docs.views import router as docs_router

APP_ROOT = Path(__file__).parent


def include_docs_router(app: FastAPI, router: APIRouter) -> None:
    print("===> settings.API_DOCS_ENABLED", settings.API_DOCS_ENABLED)
    if settings.API_DOCS_ENABLED:
        app.mount(f"{settings.API_PREFIX}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)


def setup_prometheus(app: FastAPI) -> None:
    # TODO: проверить, что prometheus-fastapi-instrumentator установлен
    print("===> settings.PROMETHEUS_ENABLED", settings.PROMETHEUS_ENABLED)
    if settings.PROMETHEUS_ENABLED:
        instrumentator = PrometheusFastApiInstrumentator(should_group_status_codes=False)
        instrumentator = instrumentator.instrument(app)
        instrumentator.expose(
            app,
            should_gzip=settings.PROMETHEUS_SHOULD_GZIP,
            name=settings.PROMETHEUS_NAME,
            tags=["Метрики"]
        )
        # TODO: остальные настройки в settings


def include_routers(app: FastAPI) -> None:
    router = APIRouter()
    include_docs_router(app, router)
    app.include_router(router)


application = FastAPI(
    title=settings.API_TITLE,
    summary=settings.API_SUMMARY,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=f"{settings.API_PREFIX}/docs/openapi.json"
)
# TODO: настроить урлы
application.include_router = partial(application.include_router, prefix=settings.API_PREFIX)
include_routers(application)
setup_prometheus(application)
