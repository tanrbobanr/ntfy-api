# --- python venv setup ------------------------------------------------
VENV := make-venv
ifeq ($(OS),Windows_NT)
	BIN := $(VENV)/Scripts
	PY := python
	PY_INSTALL := $(PY)
else
	BIN := $(VENV)/bin
	PY := python3
	PY_INSTALL := $(PY)
endif
PYEXE := $(BIN)/$(PY)
MINPYVERMAJ = 3
MINPYVERMIN = 9


# --- misc -------------------------------------------------------------
# default rule (just screams if arguments are incorrect)
.PHONY: all
all:
	$(error Please provide a target)

.PHONY: force-min
force-min:
	$(eval PY_INSTALL=python${MINPYVERMAJ}.${MINPYVERMIN})


# --- create and check venv --------------------------------------------
# create the virtual environment
$(VENV): requirements-dev.txt
	$(PY_INSTALL) -m venv $(VENV)

# ensure venv python version is correct
.PHONY: py-version
py-version: $(VENV)
	$(PYEXE) -c "import sys;assert sys.version_info>=(${MINPYVERMAJ},${MINPYVERMIN}),'($(VENV)) Python version too low'"


# --- initialize venv --------------------------------------------------
# install package requirements
.PHONY: init-package
init-package: py-version
	$(BIN)/pip install --upgrade -r requirements.txt


# install test requirements
.PHONY: init-test
init-test: py-version
	$(BIN)/pip install --upgrade -r requirements-test.txt


# install dev requirements
.PHONY: init-dev
init-dev: py-version
	$(BIN)/pip install --upgrade -r requirements-dev.txt

# install build requirements
.PHONY: init-build
init-build: init-dev
	$(BIN)/pip install --upgrade -r requirements-build.txt


# --- main rules -------------------------------------------------------
# ensure package version is new
.PHONY: package-version-check
package-version-check: init-build
	$(PYEXE) vercheck.py

# run tests
.PHONY: tests
# we don't need init-test here because tox will install the test
# requirements on a per-environment basis
tests: init-dev
	$(BIN)/tox run

# run tests (parallel)
.PHONY: tests-p
tests-p: init-dev
	$(BIN)/tox run-parallel

# run pre-commit
.PHONY: pre-commit
pre-commit: init-dev
	pre-commit run --all-files

# run all required tests, pre-commit, etc
.PHONY: required
required: clean tests pre-commit
	$(MAKE) clean

# build package for pypi
.PHONY: build
build: init-build
	$(PYEXE) -m build .

# upload to pypi
.PHONY: pypi-upload
pypi-upload: init-build
	@printf "Are you sure you want to attempt to publish this package? (Y/n)\n"
	@read -r line; line_lower=$$(echo $$line | tr "[:upper:]" "[:lower:]"); if [ $$line_lower = "n" ]; then echo "Aborting..."; exit 1; fi
	$(BIN)/twine upload --verbose --config-file .pypirc dist/*

.PHONY: release
release: clean tests pre-commit build pypi-upload
	$(MAKE) clean

.PHONY: clean
clean:
	rm -rf build dist .egg src/*.egg-info $(VENV) .coverage.*
