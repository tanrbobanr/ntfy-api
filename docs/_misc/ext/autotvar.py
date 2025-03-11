import sys
from collections.abc import Generator, Sequence
from typing import Any, ForwardRef, TypeVar, TypeVarTuple, Union

if sys.version_info >= (3, 13):
    from typing import NoDefault

import functools

from docutils.nodes import Node
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.domains.python import PyVariable
from sphinx.util.typing import ExtensionMetadata, restify

from .dataref import DataRefDocumenterMixin, DataRefPyObjectMixin

# --- DIRECTIVES -------------------------------------------------------


class PyTypeVar(DataRefPyObjectMixin, PyVariable):
    """A `PyVariable` variant that adds the `tvar` and `tvartuple`
    options. Also inherits from `RefGroupPyObjectMixin`.

    """

    option_spec = {
        **DataRefPyObjectMixin.option_spec,
        **PyVariable.option_spec,
        "is-tuple": directives.flag,
    }

    def get_signature_prefix(self, sig: str) -> Sequence[Node]:
        # 'typevar *' prefix
        if "is-tuple" in self.options:
            return addnodes.desc_annotation("typevar *", "typevar *")

        # 'typevar ' prefix
        return addnodes.desc_annotation("typevar ", "typevar ")


# --- DOCUMENTERS ------------------------------------------------------


class TVarDocumenter(DataRefDocumenterMixin):
    objtype = "tvar"
    directivetype = "typevariable"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return isinstance(member, (TypeVar, TypeVarTuple))

    @functools.cached_property
    def type(self) -> type[Union[TypeVar, TypeVarTuple]]:
        if isinstance(self.object, TypeVar):
            return TypeVar
        return TypeVarTuple

    def resolve_forward_ref(self, tp: Any) -> Any:
        if not isinstance(tp, ForwardRef):
            return tp

        if tp.__forward_evaluated__:
            return tp.__forward_value__

        # resolve it ourselves
        g = sys.modules[self.object.__module__].__dict__
        return eval(tp.__forward_code__, g, g)

    def get_typevar_signature(self) -> Generator[str, None, None]:
        obj: TypeVar = self.object

        yield repr(obj.__name__)
        yield from (
            restify(c)
            for c in map(self.resolve_forward_ref, obj.__constraints__)
        )

        bound = self.resolve_forward_ref(obj.__bound__)

        if bound:
            bound_name = getattr(bound, "__name__", repr(bound))
            yield f"bound={bound_name}"

        if obj.__covariant__:
            yield "covariant=True"

        if obj.__contravariant__:
            yield "contravariant=True"

        if sys.version_info >= (3, 12):
            if obj.__infer_variance__:
                yield "infer_variance=True"

        if sys.version_info >= (3, 13):
            if obj.__default__ != NoDefault:
                yield f"default={obj.__default__!r}"

    def get_typevartuple_signature(self) -> Generator[str, None, None]:
        obj: TypeVarTuple = self.object

        yield repr(obj.__name__)

    def get_signature(self) -> Generator[str, None, None]:
        if self.type is TypeVar:
            yield from self.get_typevar_signature()
        else:
            yield from self.get_typevartuple_signature()

    def add_directive_header(self, sig: str) -> None:
        sourcename = self.get_sourcename()
        signature = ", ".join(self.get_signature())
        super().add_directive_header(sig)
        self.add_line(
            f"   :value: {self.type.__name__}({signature})", sourcename
        )
        if self.type is TypeVarTuple:
            self.add_line("   :is-tuple:", sourcename)

    def get_doc(self) -> list[list[str]]:
        if self.object.__doc__ != self.type.__doc__:
            return super().get_doc() or []
        return []


# --- SPHINX SETUP -----------------------------------------------------


def setup(app: Sphinx) -> ExtensionMetadata:
    # required extensions
    app.setup_extension("sphinx.ext.autodoc")
    app.setup_extension("_misc.ext.dataref")

    # directives
    app.add_directive_to_domain("py", "typevariable", PyTypeVar)

    # autodocumenters
    app.add_autodocumenter(TVarDocumenter)

    return {"parallel_read_safe": True}
