"""A common credentials class used by most of the API wrapper classes.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import base64
import dataclasses
from types import MappingProxyType
from typing import Literal, Union

from .__version__ import *  # noqa: F401,F403

__all__ = ("Credentials",)


@dataclasses.dataclass(frozen=True)
class Credentials:
    """Stores access credentials.

    :param basic: Basic HTTP credentials. If a single :class:`str` is
        given, it is assumed to already be base64-encoded (encoded from
        a :class:`str` of the format ``<user>:<pass>``). If a 2-tuple is
        given, it should be of the form ``(<user>, <pass>)``.
    :type basic: str | tuple[str, str] | None, optional
    :param bearer: Bearer HTTP credentials. If both :paramref:`.basic`
        and :paramref:`.bearer` are defined, :paramref:`.bearer` will be
        used.
    :type bearer: str | None, optional

    """

    basic: Union[str, tuple[str, str], None] = None
    """See the :paramref:`~Credentials.basic` parameter."""

    bearer: Union[str, None] = None
    """See the :paramref:`~Credentials.bearer` parameter."""

    @staticmethod
    def _create_auth_header(
        auth_type: Literal["Basic", "Bearer"], credentials: str
    ) -> MappingProxyType[str, str]:
        """A helper method that creates the authentication header with
        the given authentication type and credentials.

        :param auth_type: The authentication type, either ``"Basic"`` or
            ``"Bearer"``.
        :type auth_type: typing.Literal["Basic", "Bearer"]
        :param credentials: The credentials string.
        :type credentials: str

        :return: The authentication header as an immutable mapping.
        :rtype: types.MappingProxyType[str, str]

        """
        return MappingProxyType(
            {"Authorization": f"{auth_type} {credentials}"}
        )

    def get_header(self) -> MappingProxyType[str, str]:
        """Create the authorization header with the given credentials.
        Result may be empty.

        :return: The authentication header as an immutable mapping.
        :rtype: ~types.MappingProxyType[str, str]

        :raises ValueError: If no valid credentials are present.

        """
        if self.bearer is not None:
            return self._create_auth_header("Bearer", self.bearer)
        elif isinstance(self.basic, str):
            return self._create_auth_header("Basic", self.basic)
        elif (
            self.basic
            and hasattr(self.basic, "__len__")
            and len(self.basic) == 2
            and all(isinstance(e, str) for e in self.basic)
        ):
            return self._create_auth_header(
                "Basic",
                base64.b64encode(":".join(self.basic).encode("ascii")).decode(
                    "ascii"
                ),
            )
        elif self.basic:
            raise ValueError("Invalid basic credentials")
        else:
            return MappingProxyType({})
