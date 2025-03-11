# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2025-03-10

### Changed

The majority of the library was either rewritten or had its location changed.
The 1.x.x releases should be considered incompatible with the 0.x.x releases.

## [0.0.6] - 2024-10-25

### Fixed

- Included the `httpx` library as a dependency in `pyproject.toml`.

## [0.0.5] - 2024-10-25

### Fixed

- Fixed issue where `publisher._NtfyURL.parse` was not correctly using the edited URL components.

## [0.0.4] - 2024-10-24

### Added

- `.mypy_cache/` to `.gitignore`.
- `package-data` section to `pyproject.toml`.

### Changed

- More robust URL parsing in `publisher._NtfyURL`.
- `ntfy_url` in `publisher.NtfyPublisher` was split into `url` and `topic`, to allow for the topic to be (optionally) sent separately and on a per-message basis.

## [0.0.3] - 2024-10-23

### Fixed

- `message._Message`'s `_default_serializer` method now escapes newlines.
- Trailing forward slashes are now stripped in `publisher._NtfyURL`'s `__post_init__` and `unparse_with_topic` methods, as this can affect self-hosted `ntfy` services.

## [0.0.2] - 2024-10-23

### Added

- `publisher.NtfyPublisher`'s `publish` method now returns the `httpx.Response` object.

## [0.0.1] - 2024-10-21

Initial release.
