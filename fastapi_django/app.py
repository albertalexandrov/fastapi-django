from functools import partial
from pathlib import Path

import pkg_resources
from fastapi import APIRouter, FastAPI, Depends
from starlette.staticfiles import StaticFiles

from fastapi_django.auth.authentication import auth
from fastapi_django.conf import settings
from fastapi_django.docs.views import router as docs_router

installed_packages = pkg_resources.working_set
installed_packages_list = [f"{i.key}" for i in installed_packages]

APP_ROOT = Path(__file__).parent


def include_docs_router(app: FastAPI, router: APIRouter) -> None:
    print("===> settings.API_DOCS_ENABLED", settings.API_DOCS_ENABLED)
    if settings.API_DOCS_ENABLED:
        app.mount(f"{settings.API_PREFIX}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)


def setup_prometheus(app: FastAPI) -> None:
    print("===> settings.PROMETHEUS_ENABLED", settings.PROMETHEUS_ENABLED)
    if settings.PROMETHEUS_ENABLED and "prometheus-fastapi-instrumentator" in installed_packages_list:
        from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator

        instrumentator = PrometheusFastApiInstrumentator(should_group_status_codes=False)
        instrumentator = instrumentator.instrument(app)
        instrumentator.expose(
            app, should_gzip=settings.PROMETHEUS_SHOULD_GZIP, name=settings.PROMETHEUS_NAME, tags=["Метрики"]
        )
        # TODO:
        #  остальные настройки в settings
        #  создать функцию типа get_prefixed_url


def include_routers(app: FastAPI) -> None:
    router = APIRouter()
    include_docs_router(app, router)
    app.include_router(router)


def setup_middlewares(app: FastAPI) -> None:
    for middleware in settings.MIDDLEWARES:
        print("===> middleware", middleware)
        app.add_middleware(middleware)
    #  TODO: продумать:
    #  преднастроенные миддлварь, которые задаются в строковом формате и
    #  имеют настройки ИЛИ не имеют параметров инициализации
    #  callabe миддвари, с преднастроенными при помощи partial параметрами напр:
    #   MIDDLEWARES = [
    #     partial(TrustedHostMiddleware, allowed_hosts=["localhost", "*.example.com"])
    #   ]


def get_default_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        summary=settings.API_SUMMARY,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=f"{settings.API_PREFIX}/docs/openapi.json",
        dependencies=[Depends(auth)],
    )
    # TODO: настроить урлы
    app.include_router = partial(app.include_router, prefix=settings.API_PREFIX)  # type: ignore
    include_routers(app)
    setup_prometheus(app)
    setup_middlewares(app)
    return app
