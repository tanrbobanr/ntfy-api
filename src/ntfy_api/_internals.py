"""Internals.

:copyright: (c) 2024 Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""

__author__ = "Tanner Corcoran"
__license__ = "Apache 2.0 License"
__copyright__ = "Copyright (c) 2024 Tanner Corcoran"


from typing import (
    final,
    Self,
    Any,
    Literal,
)


@final
class _UnsetType:
    def __copy__(self) -> Self:
        return self
    
    def __deepcopy__(self, memo: Any) -> Self:
        return self
    
    def __bool__(self) -> Literal[False]:
        return False
    
    def __repr__(self) -> str:
        return "<unset>"


_Unset = _UnsetType()
