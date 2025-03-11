import sys
from collections.abc import Callable
from typing import Any, Generic, TypeVar, Union

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec
del sys


_T = TypeVar("_T")
_P = ParamSpec("_P")


class InstanceCache(Generic[_T]):
    def __init__(
        self, constructor: Callable[_P, _T], /, **defaults: Any
    ) -> None:
        self._constructor = constructor
        self._instance: Union[_T, None] = None
        self._defaults = defaults

    @property
    def instance(self) -> _T:
        if self._instance is None:
            raise ValueError("instance not yet created")
        return self._instance

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        self._instance = self._constructor(*args, **self._defaults, **kwargs)
        return self._instance
