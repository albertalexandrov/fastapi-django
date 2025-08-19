"""
Tools for sending email.
"""
from typing import Any, Iterable, Sequence

from fastapi_django.conf import settings
# Imported for backwards compatibility and for the sake
# of a cleaner namespace. These symbols used to be in
# fastapi_django/core/mail.py before the introduction of email
# backends and the subsequent reorganization (See #10355)
from fastapi_django.mail.message import (
    DEFAULT_ATTACHMENT_MIME_TYPE,
    BadHeaderError,
    EmailAlternative,
    EmailAttachment,
    EmailMessage,
    EmailMultiAlternatives,
    SafeMIMEMultipart,
    SafeMIMEText,
    forbid_multi_line_headers,
    make_msgid,
)
from fastapi_django.mail.utils import DNS_NAME, CachedDnsName, get_provider, get_required, get_option

__all__ = [
    "CachedDnsName",
    "DNS_NAME",
    "EmailMessage",
    "EmailMultiAlternatives",
    "SafeMIMEText",
    "SafeMIMEMultipart",
    "DEFAULT_ATTACHMENT_MIME_TYPE",
    "make_msgid",
    "BadHeaderError",
    "forbid_multi_line_headers",
    "get_connection",
    "send_mail",
    "send_mass_mail",
    "EmailAlternative",
    "EmailAttachment",
    "outbox"
]

from fastapi_django.utils.module_loading import import_string

outbox: list = []


def get_connection(fail_silently: bool = False, provider: str = settings.DEFAULT_EMAIL_PROVIDER_ALIAS, **kw: Any):
    backend = get_required(provider, "BACKEND")
    klass = import_string(backend)
    return klass(fail_silently=fail_silently, provider=provider, **kw)


async def send_mail(
    subject: str,
    body: str,
    recipient_list: Sequence[str],
    from_email: str | None = None,
    fail_silently: bool = False,
    html_message=None,
    connection=None,
    provider: str = settings.DEFAULT_EMAIL_PROVIDER_ALIAS,
):
    """
    Если передан connection, то using игнорируется
    """
    connection = connection or get_connection(fail_silently=fail_silently, provider=provider)
    from_email = from_email or get_option(provider, "from_email")
    mail = EmailMultiAlternatives(
        subject, body, from_email, recipient_list, connection=connection
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    return await mail.send()


async def send_mass_mail(
    datatuple, fail_silently=False, connection=None, provider: str = settings.DEFAULT_EMAIL_PROVIDER_ALIAS,
):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), send
    each message to each recipient list. Return the number of emails sent.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(fail_silently=fail_silently, provider=provider)
    messages = [
        EmailMessage(subject, body, sender, recipient, connection=connection, prodiver=provider)
        for subject, body, sender, recipient in datatuple
    ]
    return await connection.send_messages(messages)
