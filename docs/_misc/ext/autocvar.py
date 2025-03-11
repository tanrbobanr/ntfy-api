from collections.abc import Sequence

from docutils.nodes import Node
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.domains.python import PyAttribute
from sphinx.ext.autodoc import AttributeDocumenter, Options
from sphinx.util.typing import ExtensionMetadata

# --- DIRECTIVES -------------------------------------------------------


class PyClassVariable(PyAttribute):
    def get_signature_prefix(self, sig: str) -> Sequence[Node]:
        return (addnodes.desc_annotation("cvar ", "cvar "),)


# --- DOCUMENTERS ------------------------------------------------------


class CVarDocumenter(AttributeDocumenter):
    objtype = "cvar"
    priority = AttributeDocumenter.priority + 1
    directivetype = "classvariable"
    option_spec = dict(AttributeDocumenter.option_spec)
    del option_spec["no-value"]

    def add_directive_header(self, sig: str) -> None:
        self.options = Options(self.options)
        self.options["no-value"] = False
        super().add_directive_header(sig)


# --- SPHINX SETUP -----------------------------------------------------


def setup(app: Sphinx) -> ExtensionMetadata:
    # required extensions
    app.setup_extension("sphinx.ext.autodoc")

    # directives
    app.add_directive_to_domain("py", "classvariable", PyClassVariable)

    # autodocumenters
    app.add_autodocumenter(CVarDocumenter)

    return {"parallel_read_safe": True}
