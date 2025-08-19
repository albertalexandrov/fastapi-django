"""
Email message and email sending related helper functions.
"""

import socket
from typing import Any

from fastapi_django.conf import settings
from fastapi_django.exceptions import ImproperlyConfigured
from fastapi_django.utils.encoding import punycode


def get_provider(provider: str) -> dict[str, Any]:
    if provider := settings.EMAIL_PROVIDERS.get(provider):
        return provider
    raise ImproperlyConfigured(f"`{provider}` отсутствует в EMAIL_PROVIDERS")


def get_options(provider: str) -> dict[str, Any]:
    return get_provider(provider).get("OPTIONS", {})


def get_option(provider: str, option: str, default: Any = None) -> Any:
    options = get_options(provider)
    return options.get(option, default)


def get_required(provider: str, param: str) -> Any:
    return get_provider(provider)[param]


# Cache the hostname, but do it lazily: socket.getfqdn() can take a couple of
# seconds, which slows down the restart of the server.
class CachedDnsName:
    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, "_fqdn"):
            self._fqdn = punycode(socket.getfqdn())
        return self._fqdn


DNS_NAME = CachedDnsName()
