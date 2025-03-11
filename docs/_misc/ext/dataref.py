import dataclasses
from collections import defaultdict
from collections.abc import Generator
from typing import Union

from docutils.nodes import Node, document
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.domains.python import PyClasslike, PyObject
from sphinx.ext.autodoc import SUPPRESS, DataDocumenter, Documenter, Options
from sphinx.util.typing import ExtensionMetadata

# --- MIXINS -----------------------------------------------------------


class DataRefPyObjectMixin(PyObject):
    """A :class:`PyObject` mixin which adds the `data-ref` option.

    The value of the option, if present, is added to the `desc` node
    attributes when the signature is handled.

    """

    option_spec = {
        "data-ref": int,
    }

    def handle_signature(
        self, sig: str, signode: addnodes.desc_signature
    ) -> tuple[str, str]:
        # set data-ref on the signode parent (desc node) if data-ref
        # is available
        if "data-ref" in self.options:
            signode.parent.attributes["data-ref"] = self.options["data-ref"]
        return super().handle_signature(sig, signode)


class DataRefDocumenterMixin(DataDocumenter):
    directivetype = "data"

    def add_ref_group(self) -> None:
        """Adds the :data-ref: option as a new line."""
        alias_id = hash((
            self.module,
            self.modname,
            self.real_modname,
            self.object,
            self.object_name,
            self.directivetype,
            self.objtype,
        ))
        self.add_line(f"   :data-ref: {alias_id}", self.get_sourcename())

    def add_content(self, more_content: Union[StringList, None]) -> None:
        sourcename = self.get_sourcename()

        Documenter.add_content(self, more_content)

        # add py:class immediately after, using
        # `self.directive.result.append` directly since we need to
        # dedent
        self.directive.result.append(
            f"{self.indent[:-3]}.. py:class:: {self.fullname}", sourcename
        )
        self.add_ref_group()

    def add_directive_header(self, sig: str) -> None:
        self.options = Options(self.options)
        self.options["annotation"] = SUPPRESS
        self.options["no-index"] = True
        super().add_directive_header(sig)
        self.add_ref_group()


# --- DIRECTIVES -------------------------------------------------------


class DataRefPyClassLike(DataRefPyObjectMixin, PyClasslike):
    """A `PyClassLike` variant that inherits from
    `RefGroupPyObjectMixin`.

    """

    option_spec = {
        **DataRefPyObjectMixin.option_spec,
        **PyClasslike.option_spec,
    }


# --- REFGROUP HANDLING ------------------------------------------------


def replace_obj_attrs(source: object, target: object) -> None:
    for k, v in source.__dict__.items():
        setattr(target, k, v)


@dataclasses.dataclass(eq=False)
class DataRef:
    py_data: Union[addnodes.desc, None] = None
    py_class: Union[addnodes.desc, None] = None

    @staticmethod
    def get_index(node: addnodes.desc) -> addnodes.index:
        return node.parent.children[node.parent.index(node) - 1]

    @staticmethod
    def get_signature(node: addnodes.desc) -> addnodes.desc_signature:
        return node.children[
            node.first_child_matching_class(addnodes.desc_signature)
        ]

    def apply(self) -> None:
        if self.py_data is None or self.py_class is None:
            return

        py_class_index = self.get_index(self.py_class)

        # replace index
        replace_obj_attrs(py_class_index, self.get_index(self.py_data))

        # set ids
        self.get_signature(self.py_data).attributes["ids"] = (
            self.get_signature(self.py_class).attributes["ids"]
        )

        # remove class and its index
        self.py_data.parent.remove(self.py_class)
        self.py_data.parent.remove(py_class_index)


def is_data_ref(node: Node) -> bool:
    if not isinstance(node, addnodes.desc):
        return False

    if node.attributes.get("data-ref") is None:
        return False

    return True


def get_data_ref_nodes(
    doctree: document,
) -> Generator[addnodes.desc, None, None]:
    yield from doctree.findall(is_data_ref)


def merge_data_refs(app: Sphinx, doctree: document) -> None:
    data_refs: defaultdict[int, DataRef] = defaultdict(DataRef)

    # find ref groups
    for node in get_data_ref_nodes(doctree):
        domain: Union[str, None] = node.attributes.get("domain")
        data_ref_id: int = node.attributes["data-ref"]

        if domain != "py":
            raise ValueError(f"Invalid domain for ref group: {domain}")

        if node.attributes.get("classes") == ["py", "class"]:
            data_refs[data_ref_id].py_class = node
        else:
            data_refs[data_ref_id].py_data = node

    # apply ref groups
    for g in data_refs.values():
        g.apply()


# --- SPHINX SETUP -----------------------------------------------------


def setup(app: Sphinx) -> ExtensionMetadata:
    # required extensions
    app.setup_extension("sphinx.ext.autodoc")

    # directives
    app.add_directive_to_domain("py", "class", DataRefPyClassLike)

    # events
    app.connect("doctree-read", merge_data_refs)

    return {"parallel_read_safe": True}
