# Contributor's Guide

This document lays out the guidelines, procedures, and general advice for
making contributions to this project. Any form of contribution is very much
appreciated! Open-source projects, like this one, relies on the support they
receive from other members of the community like yourself.

To start, please read this document to get a feel for how the project works.
This guide is split into a number of sections based on the types of
contributions you intend to make, as well as a general set of guidelines
applicable to all contributors. If you have any questions, please feel free to
contact one of the primary maintainers.

## Be Cordial

Any and all contributions are welcome, so long as everyone involved is treated
with respect and the [Code of Conduct](./CODE_OF_CONDUCT.md) is followed.

## Get Early Feedback

If you are contributing, do not feel the need to sit on your contribution until
it is perfectly polished and complete. It helps everyone involved for you to
seek feedback as early as you possibly can. Submitting an early, unfinished
version of your contribution for feedback in no way prejudices your chances of
getting that contribution accepted, and can save you from putting a lot of work
into a contribution that is not suitable for the project.

## Contribution Suitability

Our project maintainers have the last word on whether or not a contribution is
suitable for the project. All contributions will be considered carefully, but
from time to time, contributions will be rejected because they do not suit the
current goals or needs of the project.

If your contribution is rejected, don’t despair! As long as you followed these
guidelines, you will have a much better chance of getting your next
contribution accepted.

## Code Contributions

When contributing code, you’ll want to follow this general procedure:

1. Fork the repository on GitHub.

2. Create a local clone of your forked repository.

3. Run the available tests with `make tests` and confirm all tests pass on your
    system. If they don’t, you’ll need to investigate why they fail. If you’re
    unable to diagnose this yourself, raise it as a bug report by following the
    guidelines in this document: [Bug Reports](#bug-reports). Some common
    issues are:

    1. One or more of the project's supported Python versions is missing from
        your system, causing `tox` to fail. Installing the missing versions
        should resolve this issue.

    2. Your system's default Python version (e.g. `python3 --version` on unix,
        or `python --version` on Windows) is below this project's minimum
        supported Python version. To force the `make` invocation to use the
        project's minimum supported Python version for creating its virtual
        environment, use `force-min` as the **first target**.

    3. `venv` is not available for the version of Python being used to create
        the virtual environment within `make`. Ensure `venv` is available. How
        to do this varies depending on the operating system, but generally
        involves ensuring your default Python installation is not a minimal
        install.

4. Create a virtual environment (e.g. with `python3 -m venv venv`).

5. Source your virtual environment (e.g. with `source venv/bin/activate`).

6. Install the development requirements with
    `pip install -U -r requirements-dev.txt`.

7. Install the pre-commit hooks with `pre-commit install --install-hooks`.

8. Write tests that demonstrate your bug or feature. Ensure that they fail.
    This can be done by running `pytest tests`.

9. Make your changes to the repository.

10. Write tests that cover **all** parts of your code. Some exceptions may
apply (see [Code Coverage](#code-coverage)).

11. Run the entire test suite again with `make tests` and ensure all tests
    pass, including the ones you just added.

12. Add your name to [the contributors file](../CONTRIBUTORS.md) if warranted
    (see [Attribution](#attribution) for more details).

13. Commit your changes, then push to your GitHub repository. Ensure any errors
    encountered during the pre-commit invocation are resolved.

14. Send a GitHub Pull Request to the main repository’s main branch. GitHub
    Pull Requests are the expected method of code collaboration on this
    project.

The following sub-sections go into more detail on some of the points above.

### Code Review

Contributions will not be merged until they’ve been code reviewed. You should
implement any code review feedback unless you strongly object to it. In the
event that you object to the code review feedback, you should make your case
clearly and calmly. If, after doing so, the feedback is judged to still apply,
you must either apply the feedback or withdraw your contribution.

### Code Coverage

This package enforces a relatively strict 100% code coverage requirement. Some
exceptions do apply, though:

- In certain circumstances, the `no branch` pragma may be used. For example:
    ```py
    def close(self) -> None:
        """Close the connection, if it exists and is open."""
        if not self.closable_connection.is_closed():  # pragma: no branch
            self.closable_connection.close()
    ```

- In certain circumstances, when conditional imports are utilized (generally
    those predicated on `sys.version_info`), the `no cover` pragma may be used.
    For example:
    ```py
    import sys

    if sys.version_info >= (3, 11):  # pragma: no cover
        from typing import Self
    else:  # pragma: no cover
        from typing_extensions import Self
    ```

- In other circumstances, use your common sense when determining whether you
    should use a pragma statement. Worst case, the person(s) reviewing your
    code will ask that you remove the statement and ensure test coverage for
    the code in question.

### Code Style

This section covers code style expectations.

#### General Code Style

This project uses the [black](https://github.com/psf/black) code style. The
tool is included in the development requirements and can be activated on the
command-line directly or through `pre-commit run [...]` (although the latter
also runs a number of other pre-commit hooks).

Both [isort](https://github.com/PyCQA/isort) and
[flake8](https://github.com/PyCQA/flake8) are used as well to enforce styling.

#### Docstrings

This project requires that the majority of modules, functions, and classes
contain a docstring. These docstrings must use the `reStructuredText` format.
The level of documentation provided in each docstring may vary; for instance,
internal functions and classes will not be held to the same standard of
documentation as ones which are publicly exposed. All publicly-exposed objects
must have a docstring.

Sphinx is used to format documentation, and the
[sphinx_paramlinks extension](https://github.com/sqlalchemyorg/sphinx-paramlinks)
is included, so you may make use of the `:paramref:` text role.

#### File Headers

Each file should be headed with a docstring of the following form:

```py
"""[DESCRIPTION]

:copyright: (c) [YEAR] Tanner Corcoran
:license: Apache 2.0, see LICENSE for more details.

"""
```

If making changes to an existing file, do not change the copyright year. If the
file is new, however, the current year should be used.

#### Package Information

Package information is defined within the top-level `__package_info__.py` file
within the package. Each file within the package must import all content within
the `__package_info__` module with the following:

```py
from .__package_info__ import *  # noqa: F401,F403
```

Note:
- `__package_info__` is a relative import, so the statement will need to be
    slightly changed depending on the location of the file importing it.

- The `noqa` statement is not required within `__init__.py` files, as both the
    `F401` and `F403` errors are ignored for `__init__.py` files.

### Updating the Documentation

When updating the documentation (if warranted), make sure to insert your
changes to the documentation files in alphabetical order. The `autoivar`,
`autocvar`, and `autotvar` directives have been added, which should be used
for instance, class and type variables (`TypeVar` and `TypeVarTuple`)
respectively. Additionally, the `autoalias` directive has been added, and
should be used for type aliases. Use existing documentation as a general guide
for how to correctly document your changes.

### Updating the Changelog

The changelog is located within the `CHANGELOG.md` file in the project
directory. Add your modifications to the `## [Unreleased]` section as needed,
following the format specified in
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

### Attribution

If you are a new contributor, add your full name (first and last), a link to
your GitHub user, and contact email to the **bottom** of
[the contributors file](../CONTRIBUTORS.md). Do so in the pull request that
would warrant an attribution (i.e. your first code contribution pull request).
The line should be formatted as follows (using your own details instead):

> `- Tanner Corcoran [@tanrbobanr](https://github.com/tanrbobanr) <tannerbcorcoran@gmail.com>`

If you are not comfortable using your full name, you may instead use your
GitHub username:

> `- tanrbobanr [@tanrbobanr](https://github.com/tanrbobanr) <tannerbcorcoran@gmail.com>`

## Bug Reports

Bug reports are hugely important! Before you raise one, though, please check
through the [GitHub issues](../../../issues), both open and closed, to confirm
that the bug hasn’t been reported before. Duplicate bug reports are a huge
drain on the time of other contributors, and should be avoided as much as
possible. When issuing a bug report, use the `Bug Report` template, which is
accessible when creating a [new issue](../../../issues/new/choose).

## Feature Requests

Feel free to request new features for this project. Before you do, though,
please check through the [GitHub issues](../../../issues), both open and
closed, to confirm that the feature hasn't been requested before. When issuing
a feature request, use the `Feature Request` template, which is accessible when
creating a [new issue](../../../issues/new/choose).


*This contributor's guide makes use of some content, word-for-word or
paraphrased, of the
[psf/requests contributor's guide](https://requests.readthedocs.io/en/latest/dev/contributing/).*
