"""
Backend for test environment.
"""

import copy

from fastapi_django import mail
from fastapi_django.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """
    An email backend for use during test sessions.

    The test connection stores email messages in a dummy outbox,
    rather than sending them out on the wire.

    The dummy outbox is accessible through the outbox instance attribute.
    """

    async def send_messages(self, messages):
        """Redirect messages to the dummy outbox"""
        msg_count = 0
        for message in messages:  # .message() triggers header validation
            message.message()
            mail.outbox.append(copy.deepcopy(message))
            msg_count += 1
        return msg_count
