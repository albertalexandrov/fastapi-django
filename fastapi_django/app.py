from pathlib import Path

from fastapi import APIRouter, FastAPI
from starlette.staticfiles import StaticFiles

from .conf import settings
from .docs.views import router as docs_router

APP_ROOT = Path(__file__).parent


# def include_docs_router(router: APIRouter) -> APIRouter:
#     if settings.API_DOCS_ENABLED:
#         app.mount(f"{prefix}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
#         router.include_router(docs_router)


def include_routers(app: FastAPI) -> None:
    router = APIRouter()
    # if prefix := settings.API_PREFIX:
    #     router.prefix = prefix
    if settings.API_DOCS_ENABLED:
        # app.mount(f"{prefix}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)
    app.include_router(router)


application = FastAPI(
    title=settings.API_TITLE,
    summary=settings.API_SUMMARY,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    root_path=settings.APP_ROOT,
)
include_routers(application)
