"""A number of monkeypatches."""

import posixpath
from typing import Annotated, Any, get_args, get_origin

import docutils.nodes
import sphinx.addnodes
import sphinx.application
import sphinx.ext.autodoc
import sphinx.ext.intersphinx._resolve
import sphinx.ext.viewcode
import sphinx.util.inspect
import sphinx.util.typing
import sphinxcontrib_trio
from sphinx import addnodes
from sphinx.pycode import ModuleAnalyzer

# -- Sphinx monkeypatches ----------------------------------------------


def _patch_sphinx() -> None:
    # augment stringify_annotation to strip `Annotated` from annotations
    def stringify_annotation(annotation: Any, *args, **kwargs: Any) -> str:
        if get_origin(annotation) == Annotated:
            annotation = get_args(annotation)[0]
        return sphinx.util.typing.stringify_annotation(
            annotation, *args, **kwargs
        )

    sphinx.util.inspect.stringify_annotation = stringify_annotation
    sphinx.ext.autodoc.stringify_annotation = stringify_annotation


# -- viewcode monkeypatches --------------------------------------------


def _patch_viewcode_anchor() -> None:
    # Here we redefine the doctree_read function to insert the
    # viewcode_anchor at the beginning of the signode, instead of
    # appending it to the end - this moves the anchor to the top of the
    # signature instead of the bottom. This would normally mess some of
    # the alignment up, but since were using multiline signatures,
    # having the anchors at the top of the signature instead of the
    # bottom looks much more natural.
    def doctree_read(
        app: sphinx.application.Sphinx, doctree: docutils.nodes.Node
    ) -> None:
        env = app.env
        events = app.events
        if not hasattr(env, "_viewcode_modules"):
            env._viewcode_modules = {}

        def has_tag(
            modname: str, fullname: str, docname: str, refname: str
        ) -> bool:
            entry = env._viewcode_modules.get(modname, None)
            if entry is False:
                return False

            code_tags = events.emit_firstresult(
                "viewcode-find-source", modname
            )
            if code_tags is None:
                try:
                    analyzer = ModuleAnalyzer.for_module(modname)
                    analyzer.find_tags()
                except Exception:
                    env._viewcode_modules[modname] = False
                    return False

                code = analyzer.code
                tags = analyzer.tags
            else:
                code, tags = code_tags

            if entry is None or entry[0] != code:
                entry = code, tags, {}, refname
                env._viewcode_modules[modname] = entry
            _, tags, used, _ = entry
            if fullname in tags:
                used[fullname] = docname
                return True

            return False

        for objnode in list(doctree.findall(addnodes.desc)):
            if objnode.get("domain") != "py":
                continue
            names: set[str] = set()
            for signode in objnode:
                if not isinstance(signode, addnodes.desc_signature):
                    continue
                modname = signode.get("module")
                fullname = signode.get("fullname")
                refname = modname
                if env.config["viewcode_follow_imported_members"]:
                    new_modname = events.emit_firstresult(
                        "viewcode-follow-imported", modname, fullname
                    )
                    if not new_modname:
                        new_modname = sphinx.ext.viewcode._get_full_modname(
                            modname, fullname
                        )
                    modname = new_modname
                if not modname:
                    continue
                fullname = signode.get("fullname")
                if not has_tag(modname, fullname, env.docname, refname):
                    continue
                if fullname in names:
                    # only one link per name, please
                    continue
                names.add(fullname)
                pagename = posixpath.join(
                    sphinx.ext.viewcode.OUTPUT_DIRNAME,
                    modname.replace(".", "/"),
                )
                signode.insert(
                    0,
                    sphinx.ext.viewcode.viewcode_anchor(
                        reftarget=pagename, refid=fullname, refdoc=env.docname
                    ),
                )

    sphinx.ext.viewcode.doctree_read = doctree_read


def _patch_viewcode_properties() -> None:
    orig = sphinx.ext.viewcode._get_full_modname

    def _get_full_modname(modname: str, attribute: str) -> str:
        return orig(modname, attribute) or modname

    sphinx.ext.viewcode._get_full_modname = _get_full_modname


# -- sphinxcontrib-trio monkeypatches ----------------------------------


def _patch_sphinxcontrib_trio() -> None:
    # update `ExtendedCallableMixin._get_signature_prefix` to prefix
    # function signature with "method" or "function" if original
    # original prefix function returns an empty string
    _get_signature_prefix_orig = (
        sphinxcontrib_trio.ExtendedCallableMixin._get_signature_prefix
    )

    def _get_signature_prefix(
        self: sphinxcontrib_trio.ExtendedCallableMixin,
    ) -> str:
        ret = _get_signature_prefix_orig(self)
        if ret:
            return ret

        if self.objtype == "method":
            return "method "

        if self.objtype == "function":
            return "function "

        return ""

    sphinxcontrib_trio.ExtendedCallableMixin._get_signature_prefix = (
        _get_signature_prefix
    )


def apply_patches() -> None:
    _patch_sphinx()
    _patch_viewcode_anchor()
    _patch_sphinxcontrib_trio()
    _patch_viewcode_properties()
