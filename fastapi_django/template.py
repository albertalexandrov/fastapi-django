from jinja2 import Environment, Template, FileSystemLoader
from starlette.templating import Jinja2Templates

from fastapi_django.conf import settings


def get_templates() -> Jinja2Templates:
    kw = {}
    if context_processors := getattr(settings, "TEMPLATES_CONTEXT_PROCESSORS", None):
        kw["context_processors"] = context_processors
    env_options = settings.TEMPLATES_ENV_OPTIONS
    loader = FileSystemLoader(settings.TEMPLATES_DIRECTORY)
    env_options.setdefault("loader", loader)
    env_options.setdefault("autoescape", True)
    env = Environment(**env_options)
    kw["env"] = env
    return Jinja2Templates(**kw)


templates = get_templates()


def render_to_string(template_name: str, context: dict | None = None) -> str:
    template = templates.get_template(template_name)
    context = context or {}
    return template.render(**context)


def get_template(template_name: str) -> Template:
    return templates.get_template(template_name)


TemplateResponse = templates.TemplateResponse
