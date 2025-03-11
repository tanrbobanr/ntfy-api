from collections.abc import Generator, Sequence
from typing import Union

from sphinx._cli.util.colour import red
from sphinx.application import Sphinx
from sphinx.domains.python import ObjectEntry
from sphinx.util.typing import ExtensionMetadata

from .utils import FQN, StatusPrinter, traverse_module


class Coverage:
    config_values = {
        "coverage_modules": ((), {list, tuple, set}),
        "coverage_ignore": ({}, {list, tuple, set}),
    }

    def __init__(self, app: Sphinx) -> None:
        self.app = app
        self.objects: set[FQN] = set()

    @property
    def modules(self) -> Sequence[str]:
        return self.app.config["coverage_modules"]

    @property
    def ignore(self) -> Sequence[str]:
        return self.app.config["coverage_ignore"]

    def _load_objects(self) -> None:
        """Load objects from modules by traversing them statically."""
        p = StatusPrinter(
            "[COVERAGE] Traversing modules: ", not self.app.quiet
        )
        for m in self.modules:
            self.objects.update(traverse_module(m, True, p))

    def _apply_ignores(self) -> None:
        """Apply all ignored values to loaded objects."""
        p = StatusPrinter("[COVERAGE] Applying ignores: ", not self.app.quiet)

        for i in self.ignore:
            p(i)
            to_remove: set[FQN] = set()
            parts = tuple(i.rstrip(".*").split("."))

            if i.endswith(".*"):
                for o in self.objects:
                    if len(o) > len(parts) and o[: len(parts)] == parts:
                        to_remove.add(o)
            elif i.endswith("*"):
                for o in self.objects:
                    if o[: len(parts)] == parts:
                        to_remove.add(o)
            else:
                for o in self.objects:
                    if o == parts:
                        to_remove.add(o)

            self.objects.difference_update(to_remove)

        p.finish()

    def _find_used_objects(self) -> Generator[str, None, None]:
        """Find objects used within the documents."""
        seen_objects: dict[str, ObjectEntry] = self.app.env.domaindata["py"][
            "objects"
        ]

        # find aliased objects
        p = StatusPrinter("[COVERAGE] Finding aliases: ", not self.app.quiet)
        aliases: dict[str, str] = dict()
        for k, v in seen_objects.items():
            p(k)
            if v.aliased:
                aliases[k] = v.node_id

        p.finish()

        # generate used objects
        p = StatusPrinter(
            "[COVERAGE] Finding documented objects: ", not self.app.quiet
        )
        for k, v in seen_objects.items():
            p(k)
            for real, alias in aliases.items():
                if k.startswith(alias):
                    k = k.replace(alias, real, 1)
                    break
            yield k

        p.finish()

    def _remove_used_objects(self) -> None:
        p = StatusPrinter("[COVERAGE] Differencing: ", not self.app.quiet)
        used_objects = set(self._find_used_objects())
        for k in used_objects:
            p(k)
            to_remove: set[FQN] = set()
            parts = tuple(k.split("."))

            for o in self.objects:
                if o == parts:
                    to_remove.add(o)

            self.objects.difference_update(to_remove)

        p.finish()

    def _build_finished_hook(
        self, app: Sphinx, exception: Union[Exception, None]
    ) -> None:
        if exception:
            print(
                "[COVERAGE] Skipping due to exception raised by build process"
            )
            return

        self._load_objects()
        self._apply_ignores()
        self._remove_used_objects()

        for o in sorted(self.objects):
            self._warn(f"[COVERAGE] {o.joined()} ({o.obj_type.value})")

    def _warn(self, warning: str) -> None:
        if self.app.quiet:
            self.app._warning.write(f"{warning}\n")
        else:
            self.app._warning.write(f"{red(warning)}\n")
        self.app._warncount += 1

    def add_hooks(self) -> None:
        self.app.connect("build-finished", self._build_finished_hook)

    def add_config_values(self) -> None:
        for name, (default, types) in self.config_values.items():
            self.app.add_config_value(
                name=name,
                default=default,
                rebuild="",
                types=types,
            )


def setup(app: Sphinx) -> ExtensionMetadata:
    cov = Coverage(app)
    cov.add_config_values()
    cov.add_hooks()

    return {}
