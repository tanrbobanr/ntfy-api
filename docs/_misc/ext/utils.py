import ast
import enum
import importlib
import importlib.util
import os
import pathlib
import string
from collections.abc import Generator, Iterable, Mapping, Sequence
from typing import Protocol, Self, TypeAlias, Union, runtime_checkable

from sphinx._cli.util.colour import blue, bold, green

Stmt: TypeAlias = Union[
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Assign,
    ast.AnnAssign,
]
_Stmt = (
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Assign,
    ast.AnnAssign,
)


ALPHANUMERIC = set(string.ascii_letters + string.digits + "_")
RawFQNSelector: TypeAlias = Union[
    Mapping[Union[str, None, tuple[Union[str, None], ...]], "RawFQNSelector"],
    Sequence[Union[str, None]],
    bool,
    None,
]


class StatusPrinter:
    def __init__(self, prefix: str, colors: bool = True) -> None:
        self.prefix = prefix
        self._colors = colors
        self._is_first: bool = True

    def _bold(self, value: str) -> str:
        if self._colors:
            return bold(value)
        return value

    def _blue(self, value: str) -> str:
        if self._colors:
            return blue(value)
        return value

    def _green(self, value: str) -> str:
        if self._colors:
            return green(value)
        return value

    def __call__(self, msg: str) -> None:
        a = ("\033[A", "")[self._is_first]
        print(f"{a}\033[G\033[K{self._bold(self.prefix)}{self._blue(msg)}")
        self._is_first = False

    def finish(self) -> None:
        a = ("\033[A", "")[self._is_first]
        d = self._green("done")
        print(f"{a}\033[G\033[K{self._bold(self.prefix)}{d}")
        self._is_first = True


class ObjType(enum.Enum):
    m = "module"
    c = "class"
    f = "function/method"
    v = "variable/attribute"


@runtime_checkable
class HasBody(Protocol):
    body: list[ast.stmt]


class FQN(tuple[str, ...]):
    obj_type: ObjType
    has_docstring: bool

    def __new__(
        cls,
        obj_type: ObjType,
        iterable: Iterable[str] = ...,
        /,
        *,
        has_docstring: bool = False,
    ) -> Self:
        inst = super().__new__(cls, () if iterable is ... else iterable)
        inst.obj_type = obj_type
        inst.has_docstring = has_docstring
        return inst

    def __repr__(self) -> str:
        d = ("-", "+")[self.has_docstring]
        return f"[{self.obj_type.name}{d}]{self.joined()}"

    def joined(self) -> str:
        return ".".join(self)

    def prefix(self, prefix: Sequence[str]) -> Self:
        return FQN(
            self.obj_type,
            tuple(prefix) + self,
            has_docstring=self.has_docstring,
        )


class FQNSelectorType(enum.Enum):
    exact = "e"
    members = "m"
    root_and_members = "rm"


class FQNSelector(tuple[str, ...]):
    sel_type: FQNSelectorType

    def __new__(
        cls, sel_type: FQNSelectorType, iterable: Iterable[str] = ..., /
    ) -> Self:
        inst = super().__new__(cls, () if iterable is ... else iterable)
        inst.sel_type = sel_type
        return inst

    def __repr__(self) -> str:
        joined = ".".join(self)
        return f"{joined}[{self.sel_type.value}]"

    def prefix(self, prefix: Sequence[str]) -> Self:
        return FQNSelector(self.sel_type, tuple(prefix) + self)

    @classmethod
    def parse(cls, selector: RawFQNSelector) -> Generator[Self, None, None]:
        """Parse a raw selector value into zero or more
        :class:`FQNSelector` instances.

        Each :class:`FQNSelector` uses one of three possible
        :class:`FQNSelectorType`s:

        * exact, where only an exact match will be counted

        * members, where only the members of the FQN (and not the
          root FQN itself) will be counted

        * root and members, where both the root and members are
          counted

        A raw selector looks like this:
        .. code:: python
            {
                "a1.b1": {                   # keys can be one or more
                                             # FQN segments, separated
                                             # by `.`
                    None: None,              # the FQN a1.b1 (exact)
                    "c1": None,              # the FQN a1.b1.c1 (exact)
                    "c2": True,              # the FQN a1.b1.c2 (root
                                             # and members)
                    "c3": False,             # the FQN a1.b1.c3
                                             # (members)
                    "c4": (                  # when sequences are used
                                             # as values, all contents
                                             # are exact matches
                        "d1",                # the FQN a1.b1.c4.d1
                                             # (exact)
                        "d2",                # the FQN a1.b1.c4.d1
                                             # (exact)
                    ),
                    "c5": {
                        (None, "d3"): False  # the FQNs a1.b1.c5
                                             # (members) and
                                             # a1.b1.c5.d3 (members)
                    }
                }
            }

        """
        # exact
        if selector is None:
            yield cls(FQNSelectorType.exact)
            return

        # members
        if selector is False:
            yield cls(FQNSelectorType.members)
            return

        # root and members
        if selector is True:
            yield cls(FQNSelectorType.root_and_members)
            return

        # sequence of exact matches
        if isinstance(selector, Sequence):
            for v in selector:
                if v is None:
                    yield cls(FQNSelectorType.exact)
                    continue
                yield cls(FQNSelectorType.exact, v.split("."))
            return

        # mapping of selectors
        if isinstance(selector, Mapping):
            for k, v in selector.items():
                # referring to parent
                if k is None:
                    yield from cls.parse(v)
                    continue

                # k is multiple FQN items and v is another raw FQN
                # selection
                if isinstance(k, tuple):
                    k_parts: tuple[Union[None, list[str]]] = tuple(
                        k2 if k2 is None else k2.split(".") for k2 in k
                    )
                    for v2 in cls.parse(v):
                        for k2 in k_parts:
                            yield v2.prefix(k2 or ())
                    continue

                # k is an FQN item and v is another raw FQN selection
                if isinstance(k, str):
                    k_parts = k.split(".")
                    for v2 in cls.parse(v):
                        yield v2.prefix(k_parts)

    def find_matches(
        self, fqns: Iterable[FQN]
    ) -> Generator[tuple[FQN, bool], None, None]:
        if self.sel_type is FQNSelectorType.exact:
            for fqn in fqns:
                yield (fqn, fqn == self)
            return

        if self.sel_type is FQNSelectorType.members:
            for fqn in fqns:
                yield (fqn, len(fqn) > len(self) and fqn[: len(self)] == self)
            return

        if self.sel_type is FQNSelectorType.root_and_members:
            for fqn in fqns:
                yield (fqn, fqn[: len(self)] == self)
            return

    def get_matches(self, fqns: Iterable[FQN]) -> Generator[FQN, None, None]:
        for fqn, is_match in self.find_matches(fqns):
            if is_match:
                yield fqn


def expand_assign_target(target: ast.expr) -> Generator[str, None, None]:
    if isinstance(target, ast.Name):
        yield target.id
        return

    if isinstance(target, (ast.List, ast.Tuple)):
        for el in target.elts:
            yield from expand_assign_target(el)


def is_str_expr(value: ast.expr) -> bool:
    return (
        isinstance(value, ast.Expr)
        and isinstance(value.value, ast.Constant)
        and isinstance(value.value.value, str)
    )


def has_docstring(value: HasBody) -> bool:
    return not not (value.body and is_str_expr(value.body[0]))


def traverse_stmt(
    stmt: Stmt, nxt: Union[ast.expr, None] = None
) -> Generator[FQN, None, None]:
    if not isinstance(stmt, _Stmt):
        return

    if isinstance(stmt, ast.Module):
        yield FQN(ObjType.m, (), has_docstring=has_docstring(stmt))
        max_index = len(stmt.body) - 1
        for i, child in enumerate(stmt.body):
            yield from traverse_stmt(
                child, (None if i == max_index else stmt.body[i + 1])
            )
        return

    if isinstance(stmt, ast.ClassDef):
        yield FQN(ObjType.c, (stmt.name,), has_docstring=has_docstring(stmt))
        max_index = len(stmt.body) - 1
        for i, child in enumerate(stmt.body):
            yield from (
                o.prefix((stmt.name,))
                for o in traverse_stmt(
                    child, (None if i == max_index else stmt.body[i + 1])
                )
            )
        return

    if isinstance(stmt, ast.Assign):
        d = nxt is not None and is_str_expr(nxt)
        for target in stmt.targets:
            yield from (
                FQN(ObjType.v, (x,), has_docstring=d)
                for x in expand_assign_target(target)
            )
        return

    if isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name):
            yield FQN(
                ObjType.v,
                (stmt.target.id,),
                has_docstring=(nxt is not None and is_str_expr(nxt)),
            )
        return

    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
        yield FQN(ObjType.f, (stmt.name,), has_docstring=has_docstring(stmt))
        return


def iter_module_py_files(
    module_path: pathlib.Path,
) -> Generator[pathlib.Path, None, None]:
    if module_path.is_file():
        yield module_path
        return

    for dirpath, _, filenames in os.walk(module_path):
        for f in filenames:
            if f.endswith(".py") or f.endswith(".pyi"):
                yield pathlib.Path(dirpath, f)


def get_module_path(module_name: str) -> pathlib.Path:
    module_path = pathlib.Path(importlib.util.find_spec(module_name).origin)
    if module_path.name in {"__init__.py", "__init__.pyi"}:
        return module_path.parent
    return module_path


def traverse_module(
    module_name: str,
    show_progress: bool = False,
    status_printer: Union[StatusPrinter, None] = None,
) -> Generator[FQN, None, None]:
    module_path = get_module_path(module_name)
    module_name_parts = tuple(module_name.split("."))

    p = status_printer or StatusPrinter("Traversing modules: ")

    for file_path in iter_module_py_files(module_path):
        # get prefix
        rel_path = file_path.relative_to(module_path)
        if rel_path.name in {"__init__.py", "__init__.pyi"}:
            rel_path = rel_path.parent
        else:
            rel_path = rel_path.parent.joinpath(rel_path.name.split(".")[0])

        prefix = module_name_parts + rel_path.parts

        with file_path.open("rb") as infile:
            tree = ast.parse(infile.read())

        for i, o in enumerate(o.prefix(prefix) for o in traverse_stmt(tree)):
            if show_progress:
                p(repr(o))
            yield o

    if show_progress:
        p.finish()
