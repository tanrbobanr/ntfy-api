"""A wrapper around the ntfy API.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__title__ = "ntfy-api"
__author__ = "Tanner Corcoran"
__email__ = "tannerbcorcoran@gmail.com"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"
__version__ = "0.0.6"
__description__ = "A wrapper around the ntfy API."
__url__ = "https://github.com/tanrbobanr/ntfy-api"
__download_url__ = "https://pypi.org/project/ntfy-api"


from .actions import (
    ViewAction,
    BroadcastAction,
    HTTPAction,
)
from .enums import (
    Priority,
    HTTPMethod,
    Tag,
)
from .publisher import (
    Message,
    NtfyPublisher,
)
from .subscriber import (
    Attachment,
    MessageData,
    NtfySubscriber,
)


__all__ = (
    "ViewAction",
    "BroadcastAction",
    "HTTPAction",
    "Priority",
    "HTTPMethod",
    "Tag",
    "Message",
    "NtfyPublisher",
    "Attachment",
    "MessageData",
    "NtfySubscriber",
)
