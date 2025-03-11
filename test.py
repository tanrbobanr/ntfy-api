from typing import *
from docs._misc.ext.utils import ObjType
import re
import functools


class FQNCmpExprError(Exception):
    pass


class FQN(tuple[str, ...]):
    obj_type: ObjType
    has_docstring: bool

    def __new__(
        cls, obj_type: ObjType, iterable: Iterable[str] = ..., /, *,
        has_docstring: bool = False
    ) -> Self:
        inst = super().__new__(cls, iterable)
        inst.obj_type = obj_type
        inst.has_docstring = has_docstring
        return inst

    def __repr__(self) -> str:
        els = ".".join(self)
        d = ("-", "+")[self.has_docstring]
        return f"[{self.obj_type.name}{d}]{els}"

    def joined(self) -> str:
        return ".".join(self)

    _match_replacements: dict[str, str] = {
        r"<<\.": r"(?:.+\.)?",
        r"<\.": r".+\.",
        r"\.>>": r"(?:\..+)?",
        r"\.>": r"\..+",
        r"\*": r"\w+",
        r"\.<>\.": r"\.\w+\.",
    }

    @classmethod
    @functools.lru_cache()
    def _parse_matching_expr(cls, cmpexpr: str) -> re.Pattern:
        cmpexpr = re.escape(cmpexpr)
        for o, n in cls._match_replacements.items():
            cmpexpr = cmpexpr.replace(o, n)
        return re.compile(cmpexpr)

        # re_parts: list[str] = list()
        # exprs = cmpexpr.split(".")

        # # validity checks
        # for es, beg in (
        #     ("<", "<<", True),
        #     (">", ">>", False),
        # ):
        #     b = ("end", "beginning")[beg]
        #     for e in es:
        #         if exprs.count(e) > 1:
        #             raise FQNCmpExprError(
        #                 f"Comparison expression: matching section: the `{e}'"
        #                 f" expression may only be used once and at the {b} of"
        #                 " the section."
        #             )
        #     if e in exprs:
        #         if beg:
        #             if 
            


        # for i, e in enumerate(exprs):
        #     if e == "<":
        #         re_parts.append(r".*")
        #         continue

        #     if e == ">":
        #         re_parts.append(r"\..+")
        #         continue

        #     if e == "<<":
        #         re_parts.append("^")

    _constraint_fns: dict[str, Callable[[ObjType, bool], bool]] = {
        "m": lambda o, d: o is ObjType.m,
        "c": lambda o, d: o is ObjType.c,
        "f": lambda o, d: o is ObjType.f,
        "v": lambda o, d: o is ObjType.v,
        "M": lambda o, d: o is not ObjType.m,
        "C": lambda o, d: o is not ObjType.c,
        "F": lambda o, d: o is not ObjType.f,
        "V": lambda o, d: o is not ObjType.v,
        "-": lambda o, d: not d,
        "+": lambda o, d: d,
    }

    def matches(self, cmpexpr: str) -> bool:
        # <   ->  matches to the beginning of the FQN (1+)
        # <<  ->  matches to the beginning of the FQN (0+)
        # >   ->  matches to the end of the FQN (1+)
        # >>  ->  matches to the end of the FQN (0+)
        # *   ->  matches any segment (whole or part)
        # <>  ->  matches between two segments
        # **  ->  matches entire name
        # []  ->  specifies constraints
        # CONSTRAINTS:
        #   m  ->  is module
        #   c  ->  is class
        #   f  ->  is function/method
        #   v  ->  is variable/attribute
        #   M  ->  is not module
        #   C  ->  is not class
        #   F  ->  is not function/method
        #   V  ->  is not variable/attribute
        #   -  ->  does not have docstring
        #   +  ->  has docstring

        # has constraints
        if cmpexpr.startswith("["):
            try:
                constraints, cmpexpr = cmpexpr.split("]")
            except Exception:
                raise FQNCmpExprError(
                    "Comparison expression: begins with `[', indicating the"
                    " start of a constraints section, but does not include"
                    " exactly one `]', indicating the end of the constraints"
                    f" section: {cmpexpr!r}"
                )

            # iterate over constraints
            for c in constraints[1:]:
                # get and call constraint function
                f = self._constraint_fns.get(c)
                if not f:
                    raise FQNCmpExprError(
                        "Comparison expression: constraints section: includes"
                        f" unknown constraint {c!r}: '{constraints}]{cmpexpr}'"
                    )
                if not f(self.obj_type, self.has_docstring):
                    return False

        # handle **
        if "**" in cmpexpr:
            if cmpexpr == "**":
                return True
            raise FQNCmpExprError(
                "Comparison expression: matching section: the `**' specifier"
                " may only be used if it is the only value in the matching"
                " section"
            )

        return not not self._parse_matching_expr(cmpexpr).match(self.joined())


f = FQN(ObjType.v, ("src", "ntfy_api", "enums_x", "Tag", "sub", "_100"), has_docstring=True)



# import cProfile
# import pstats

# with cProfile.Profile() as pr:
#     for _ in range(1_000_000):
#         FQN(ObjType.v, ("src", "ntfy_api", "enums_x", "Tag", "sub", "_100")).matches('<.ntfy_api.*.<>.sub.>>')


# pstats.Stats(pr).sort_stats(pstats.SortKey.TIME).print_stats()



# import timeit
# f = FQN(ObjType.v, ("src", "ntfy_api", "enums_x", "Tag", "sub", "_100"))
# print(timeit.timeit("f.matches('<.ntfy_api.*.<>.sub.>>')", globals=globals(), number=1_000_000))

# print(FQN.matches.cache_info())


        

