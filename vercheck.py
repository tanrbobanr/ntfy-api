"""Ensure this package's version is not already in use"""

import os
import sys
import importlib
from typing import Any

import httpx
import packaging.version
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_current_version() -> str:
    packages = os.listdir("src")
    modules = tuple(
        importlib.import_module(f"src.{p}")
        for p in packages
    )
    versions = tuple(
        str(packaging.version.Version(v)) for v in
        (getattr(m, "__version__") for m in modules)
        if v is not None
    )
    if len(set(versions)) > 1:
        raise ValueError("Module versions differ")
    return versions[0]


def get_package_name() -> str:
    try:
        with open("pyproject.toml", "rb") as infile:
            return tomllib.load(infile)["project"]["name"]
    except Exception as exc:
        raise RuntimeError(
            "Unable to get package name from pyproject.toml file"
        ) from exc


def get_releases() -> frozenset[str]:
    package_name = get_package_name()
    try:
        resp: dict[str, Any] = httpx.get(
            f"https://pypi.org/pypi/{package_name}/json"
        ).json()
    except Exception as exc:
        raise RuntimeError(
            "Request failed when attempting to retrieve pacakge info"
        ) from exc
    if resp.get("message") == "Not Found":
        return frozenset()
    try:
        releases: dict[str, Any] = resp["releases"]
        return frozenset(releases.keys())
    except Exception as exc:
        raise RuntimeError(
            f"Unable to get releases from the package info"
        ) from exc


def main() -> None:
    if get_current_version() in get_releases():
        raise ValueError("Version reused")


if __name__ == "__main__":
    main()
