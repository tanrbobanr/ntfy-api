"""Package information for this module.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

import sys
from typing import Any, Final, final

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


__all__ = (
    "__author__",
    "__author_email__",
    "__cookie__",
    "__copyright__",
    "__description__",
    "__download_url__",
    "__email__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__release__",
    "version_info",
)


__author__ = "Tanner Corcoran"
"""The package author.

This value is imported into all modules within this package.

"""


__author_email__ = "tannerbcorcoran@gmail.com"
"""The primary contact email of the package author.

This value is imported into all modules within this package.

"""


__cookie__ = "\u2728 \U0001f36a \u2728"
"""A cookie, just for you!

This value is imported into all modules within this package.

"""


__copyright__ = "Copyright (c) 2024 Tanner Corcoran"
"""The package copyright.

This value is imported into all modules within this package.

"""


__description__ = "A wrapper around the `ntfy <https://ntfy.sh>`_ API."
"""A short description of this project.

This value is imported into all modules within this package.

"""


__download_url__ = "https://pypi.org/project/ntfy-api"
"""The download URL for this package.

This value is imported into all modules within this package.

"""


__email__ = "tannerbcorcoran@gmail.com"
"""The primary contact email of the package author.

This value is the same as :attr:`__author_email__` and is simply used
for compatability. It is imported into all modules within this package.

"""


__license__ = "Apache 2.0 License"
"""The package copyright.

This value is imported into all modules within this package.

"""


__title__ = "ntfy-api"
"""The package name/title.

.. note::
    This value may be different than the *module* name.

This value is imported into all modules within this package.

"""


__url__ = "https://github.com/tanrbobanr/ntfy-api"
"""The URL to the package source repository.

This value is imported into all modules within this package.

"""


@final
class _version_info(tuple[int, int, int, int, int, int]):  # pragma: no cover
    """A version tuple implementation in many ways similar to
    :py:obj:`sys.version_info`. Acts as a singleton.

    Composed of :meth:`major`, :meth:`minor`, :meth:`micro`,
    :meth:`rc`, :meth:`post`, and :meth:`dev` versions (in that order).

    """

    __instance: Self

    def __new__(
        cls, major: int, minor: int, micro: int, rc: int, post: int, dev: int
    ) -> Self:
        if not hasattr(cls, "_version_info__instance"):
            cls.__instance = super().__new__(
                cls, (major, minor, micro, rc, post, dev)
            )
        return cls.__instance

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, memo: Any) -> Self:
        return self

    if sys.version_info >= (3, 10):
        __match_args__: Final = (
            "major",
            "minor",
            "micro",
            "rc",
            "post",
            "dev",
        )

    @property
    def major(self) -> int:
        """The major version (compatability)."""
        return self[0]

    @property
    def minor(self) -> int:
        """The minor version (features)."""
        return self[1]

    @property
    def micro(self) -> int:
        """The micro version (patches)."""
        return self[2]

    @property
    def rc(self) -> int:
        """The release candidate version."""
        return self[3]

    @property
    def post(self) -> int:
        """The post-release version."""
        return self[4]

    @property
    def dev(self) -> int:
        """The dev-release version."""
        return self[5]

    def version_str(self) -> str:
        """The version str, e.g. ``0.4.2``."""
        return f"{self[0]}.{self[1]}.{self[2]}"

    def release_str(self) -> str:
        """The release str, e.g. ``0.4.2.post3.dev1``."""
        optional_part = "".join(
            f".{k}{v}"
            for k, v in {
                "rc": self[3],
                "post": self[4],
                "dev": self[5],
            }.items()
            if v
        )
        return f"{self.version_str()}{optional_part}"


version_info: _version_info = _version_info(1, 0, 0, 1, 0, 0)
"""The version information. In many ways similar to
:py:obj:`sys.version_info`.

This value is imported into all modules within this package.

"""


__version__ = version_info.version_str()
"""The package version.

.. _version specifiers: https://packaging.python.org/en/latest/\
specifications/version-specifiers/#version-specifiers

This corresponds to the package release segment (see
`version specifiers`_ for more information).

This value is imported into all modules within this package.

"""


__release__ = version_info.release_str()
"""The package release.

.. _version specifiers: https://packaging.python.org/en/latest/\
specifications/version-specifiers/#version-specifiers

This corresponds to the package release, pre-release, post-release, and
development release segments (see `version specifiers`_ for more
information).

.. note::
    This value *may* differ from :attr:`__version__`, as
    :attr:`__version__` doesn't include the pre-, post-, or dev-release
    segments.

This value is imported into all modules within this package.

"""
