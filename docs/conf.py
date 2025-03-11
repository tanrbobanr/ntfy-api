import os
import sys

try:  # put inside a try-except block to stop flake8 E402
    sys.path.insert(0, os.path.abspath("../src"))
    sys.path.append(".")
except Exception:
    pass

import _misc

from ntfy_api.__version__ import __author__ as pkg_author
from ntfy_api.__version__ import __copyright__ as pkg_copyright
from ntfy_api.__version__ import __title__ as pkg_title
from ntfy_api.__version__ import __version__ as pkg_version

HTML_BASEURL = "https://docs.tannercorcoran.dev/python/ntfy-api"


# --- Project information ----------------------------------------------
# /en/master/usage/configuration.html#project-information

project = pkg_title
copyright = pkg_copyright
author = pkg_author
release = version = pkg_version

# --- General configuration --------------------------------------------
# /en/master/usage/configuration.html#general-configuration

needs_sphinx = "8.0"
extensions = [
    # builtin
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    # external
    "sphinx_paramlinks",
    "sphinxcontrib_trio",
    # custom
    "_misc.ext.autoivar",
    "_misc.ext.autocvar",
    "_misc.ext.autotvar",
    "_misc.ext.autoalias",
    "_misc.ext.viewcode_outdir",
    "_misc.ext.coverage",
]
exclude_patterns = ["_build"]
default_role = "literal"
nitpicky = True
nitpick_ignore = (
    ("py:class", "optional"),
    ("py:class", "httpx.Response"),
    ("py:class", "httpx.Client"),
)

# --- Options for HTML output ------------------------------------------
# /en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = f"{pkg_title} documentation"
html_short_title = f"{pkg_title}-{release}"
html_use_index = False
html_show_sourcelink = False
html_static_path = ["_static"]
html_css_files = [f"styles/{file}" for file in os.listdir("_static/styles")]
html_baseurl = ("", HTML_BASEURL)[
    not not os.environ.get("SPHINX_HTML_BUILD_FOR_RELEASE")
]

# --- Options for Autodoc ----------------------------------------------
# /en/master/usage/extensions/autodoc.html#configuration

autodoc_typehints_format = "short"
autodoc_member_order = "bysource"
autodoc_type_aliases = {
    "ReceivedAction": "ntfy_api.actions.ReceivedAction",
}

# --- Options for intersphinx ------------------------------------------
# /en/master/usage/extensions/intersphinx.html#configuration

intersphinx_timeout = 5
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "websockets": ("https://websockets.readthedocs.io/en/stable/", None),
    # httpx doesn't currently serve an objects.inv file
    # "httpx": ("https://www.python-httpx.org/", None),
}

# --- Options for viewcode ---------------------------------------------
# /en/master/usage/extensions/viewcode.html#configuration

viewcode_line_numbers = True
viewcode_output_dirname = "modules"  # added by _misc.ext.viewcode_outdir


# --- Options for _misc.ext.coverage -----------------------------------

coverage_modules = ("ntfy_api",)
coverage_ignore = (
    "ntfy_api",
    "ntfy_api.__package_info__",
    "ntfy_api.__package_info__.__all__",
    "ntfy_api.__package_info__._version_info.__copy__",
    "ntfy_api.__package_info__._version_info.__deepcopy__",
    "ntfy_api.__package_info__._version_info.__instance",
    "ntfy_api.__package_info__._version_info.__new__",
    "ntfy_api._internals",
    "ntfy_api._internals.ClearableQueue.queue",
    "ntfy_api._internals.StrTuple",
    "ntfy_api._internals.URL._unparse",
    "ntfy_api._internals.WrappingDataclass.__init_subclass__",
    "ntfy_api._internals.WrappingDataclass._context",
    "ntfy_api._internals.WrappingDataclass._get_context",
    "ntfy_api._internals._SECURE_URL_SCHEMES",
    "ntfy_api.actions",
    "ntfy_api.actions._Action.__init_subclass__",
    "ntfy_api.actions._Action._action",
    "ntfy_api.actions._Action._context",
    "ntfy_api.actions._Action._default_serializer",
    "ntfy_api.actions._Action._get_context",
    "ntfy_api.actions._Action._serialize",
    "ntfy_api.actions.__all__",
    "ntfy_api.client",
    "ntfy_api.client.NtfyClient.__post_init__",
    "ntfy_api.client.NtfyClient._auth_header",
    "ntfy_api.client.NtfyClient._http_client",
    "ntfy_api.client.NtfyClient._url",
    "ntfy_api.client.__all__",
    "ntfy_api.creds",
    "ntfy_api.creds.Credentials._create_auth_header",
    "ntfy_api.creds.__all__",
    "ntfy_api.enums",
    "ntfy_api.enums.Event.*",
    "ntfy_api.enums.HTTPMethod.*",
    "ntfy_api.enums.Priority.*",
    "ntfy_api.enums.Tag.*",
    "ntfy_api.enums.__all__",
    "ntfy_api.errors",
    "ntfy_api.errors.APIError.__init__",
    "ntfy_api.errors.__all__",
    "ntfy_api.filter",
    "ntfy_api.filter._Filter.__init_subclass__",
    "ntfy_api.filter._Filter._context",
    "ntfy_api.filter._Filter._get_context",
    "ntfy_api.filter._Filter._serialize",
    "ntfy_api.filter._Filter._serializer",
    "ntfy_api.filter.__all__",
    "ntfy_api.message",
    "ntfy_api.message.Message.__post_init__",
    "ntfy_api.message.Message._actions_serializer",
    "ntfy_api.message.Message._ignore",
    "ntfy_api.message.Message._tags_serializer",
    "ntfy_api.message._Message.__init_subclass__",
    "ntfy_api.message._Message._context",
    "ntfy_api.message._Message._default_serializer",
    "ntfy_api.message._Message._get_context",
    "ntfy_api.message._Message._serialize",
    "ntfy_api.message._ReceivedMessage._parse_actions",
    "ntfy_api.message._ReceivedMessage._parse_tags",
    "ntfy_api.message.__all__",
    "ntfy_api.subscription",
    "ntfy_api.subscription.NtfySubscription.__post_init__",
    "ntfy_api.subscription.NtfySubscription._auth_header",
    "ntfy_api.subscription.NtfySubscription._thread",
    "ntfy_api.subscription.NtfySubscription._thread_fn",
    "ntfy_api.subscription.NtfySubscription._url",
    "ntfy_api.subscription.NtfySubscription._ws_conn",
    "ntfy_api.subscription.__all__",
    "ntfy_api.subscription.logger",
)

# --- Apply patches ----------------------------------------------------

_misc.patches.apply_patches()
