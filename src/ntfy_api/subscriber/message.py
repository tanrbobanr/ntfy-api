"""The message module for the subscriber package.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"

import sys
import dataclasses
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from typing import (
    Any,
    Literal,
    Optional,
    Protocol
)


class Attachment(Protocol):
    """Protocol defining the interface for an attachment in a received message.

    Attributes:
        name: Name of the attachment
        url: URL of the attachment
        type: Mime type of the attachment (only if uploaded to ntfy server)
        size: Size in bytes (only if uploaded to ntfy server)
        expires: Expiry date as Unix timestamp (only if uploaded to ntfy server)
    """
    name: str
    url: str
    type: Optional[str]
    size: Optional[int]
    expires: Optional[int]


class MessageData(Protocol):
    """Protocol defining the interface for a message received from the ntfy server.

    Attributes:
        id: Randomly chosen message identifier
        time: Message datetime as Unix timestamp
        event: Type of event (open, message, keepalive, poll_request)
        topic: Topics the message is associated with (comma-separated)
        message: Messag body (always present in message events)
        expires: When the message will be deleted (if not Cache: no)
        title: Message title (defaults to ntfy.sh/<topic>)
        tags: List of tags that may map to emojis
        priority: Message priority (1=min, 3=default, 5=max)
        click: Website opened when notification is clicked
        actions: Action buttons that can be displayed
        attachment: Details about an attachment if present
    """
    id: str
    time: int
    event: Literal["open", "message", "keepalive", "poll_request"]
    topic: str
    message: Optional[str]
    expires: Optional[int]
    title: Optional[str]
    tags: Optional[list[str]]
    priority: Optional[int]
    click: Optional[str]
    actions: Optional[list[dict[str, Any]]]
    attachment: Optional[Attachment]
    content_type: Optional[str] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Create a MessageData instance from JSON data.

        Args:
            data: Dictionary containing message data from the server

        Returns:
            MessageData: A new MessageData instance
        """
        ...


@dataclasses.dataclass(eq=False, frozen=True)
class _Attachment(Attachment):
    """Private implementation of the Attachment protocol."""
    name: str
    url: str
    type: Optional[str] = None
    size: Optional[int] = None
    expires: Optional[int] = None


@dataclasses.dataclass(eq=False, frozen=True)
class _MessageData(MessageData):
    """Private implementation of the MessageData protocol."""
    id: str
    time: int
    event: Literal["open", "message", "keepalive", "poll_request"]
    topic: str
    message: Optional[str] = None
    expires: Optional[int] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = None
    priority: Optional[int] = None
    click: Optional[str] = None
    actions: Optional[list[dict[str, Any]]] = None
    attachment: Optional[Attachment] = None
    content_type: Optional[str] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Create a MessageData instance from JSON data.

        Args:
            data: Dictionary containing message data from the server

        Returns:
            MessageData: A new MessageData instance
        """
        # Handle attachment if present
        attachment_data = data.pop("attachment", None)
        attachment = (
            _Attachment(**attachment_data)
            if attachment_data else None
        )

        # Create message instance with remaining data
        return cls(**data, attachment=attachment)
