import ssl
import threading

from aiosmtplib import SMTP, SMTPException, SMTPServerDisconnected

from fastapi_django.conf import settings
from fastapi_django.mail.backends.base import BaseEmailBackend
from fastapi_django.mail.message import sanitize_address
from fastapi_django.mail.utils import DNS_NAME, get_required, get_options


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the SMTP network connection.

    TODO: пока не понял, что делать с ssl, tls
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        fail_silently: bool = False,
        timeout: int | float | None = None,
        provider: str = settings.DEFAULT_EMAIL_PROVIDER_ALIAS,
    ):
        super().__init__(fail_silently=fail_silently, provider=provider)
        self.host = host or get_required(provider, "HOST")
        self.port = port or get_required(provider, "PORT")
        options = get_options(provider)
        self.username = options.get("username") if username is None else username
        self.password = options.get("password") if password is None else password
        self.timeout = options.get("timeout") if timeout is None else timeout
        self.connection = None
        self._lock = threading.RLock()

    async def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {"local_hostname": DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout
        try:
            self.connection = SMTP(hostname=self.host, port=self.port, **connection_params)
            await self.connection.connect()
            # если я правильно понял, работа с TLS происходит под капотом
            if self.username and self.password:
                await self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    async def close(self):
        """Close the connection to the email server."""
        if self.connection is None:
            return
        try:
            try:
                await self.connection.quit()
            except (ssl.SSLError, SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                await self.connection.close()
            except SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    async def send_messages(self, email_messages) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = await self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            try:
                for message in email_messages:
                    sent = await self._send(message)
                    if sent:
                        num_sent += 1
            finally:
                if new_conn_created:
                    await self.close()
        return num_sent

    async def _send(self, email_message) -> bool:
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [
            sanitize_address(addr, encoding) for addr in email_message.recipients()
        ]
        message = email_message.message()
        try:
            await self.connection.sendmail(
                from_email, recipients, message.as_bytes(linesep="\r\n")
            )
        except SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
