from functools import partial
from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.staticfiles import StaticFiles

from .conf import settings
from .docs.views import router as docs_router

APP_ROOT = Path(__file__).parent


def include_docs_router(app: FastAPI, router: APIRouter) -> None:
    if settings.API_DOCS_ENABLED:
        app.mount(f"{settings.API_PREFIX}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)


def include_routers(app: FastAPI) -> None:
    router = APIRouter(prefix=settings.API_PREFIX)
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
include_routers(application)
application.include_router = partial(application.include_router, prefix=settings.API_PREFIX)
