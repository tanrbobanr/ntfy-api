import sphinx.ext.viewcode
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.typing import ExtensionMetadata


def config_inited(app: Sphinx, config: Config) -> None:
    sphinx.ext.viewcode.OUTPUT_DIRNAME = config["viewcode_output_dirname"]


def setup(app: Sphinx) -> ExtensionMetadata:
    app.setup_extension("sphinx.ext.viewcode")

    app.add_config_value(
        "viewcode_output_dirname",
        sphinx.ext.viewcode.OUTPUT_DIRNAME,
        "env",
        str,
        "Where in the final build viewcode should place the source code",
    )

    app.connect("config-inited", config_inited)
