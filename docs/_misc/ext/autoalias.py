from collections.abc import Sequence
from typing import Any, Union

from docutils.nodes import Node
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.domains.python import PyVariable
from sphinx.util import inspect
from sphinx.util.typing import ExtensionMetadata, restify

from .dataref import DataRefDocumenterMixin, DataRefPyObjectMixin

# --- DIRECTIVES -------------------------------------------------------


class PyTypeAlias(DataRefPyObjectMixin, PyVariable):
    option_spec = {
        **DataRefPyObjectMixin.option_spec,
        **PyVariable.option_spec,
    }

    def get_signature_prefix(self, sig: str) -> Sequence[Node]:
        return addnodes.desc_annotation("type alias ", "type alias ")


# --- DOCUMENTERS ------------------------------------------------------


class AliasDocumenter(DataRefDocumenterMixin):
    objtype = "alias"
    directivetype = "typealias"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return inspect.isgenericalias(member)

    def add_content(self, more_content: Union[StringList, None]) -> None:
        sourcename = self.get_sourcename()

        # format alias portion
        if getattr(self.config, "autodoc_typehints_format") == "short":
            alias = restify(self.object, "smart")
        else:
            alias = restify(self.object)

        self.add_line(f"An alias of {alias}.", sourcename)
        self.add_line("", sourcename)
        self.add_line("", sourcename)

        super().add_content(more_content)


# --- SPHINX SETUP -----------------------------------------------------


def setup(app: Sphinx) -> ExtensionMetadata:
    # required extensions
    app.setup_extension("sphinx.ext.autodoc")
    app.setup_extension("_misc.ext.dataref")

    # directives
    app.add_directive_to_domain("py", "typealias", PyTypeAlias)

    # autodocumenters
    app.add_autodocumenter(AliasDocumenter)

    return {"parallel_read_safe": True}
