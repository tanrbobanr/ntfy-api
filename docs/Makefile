# ---------------------------------
# Makefile for Sphinx documentation
# ---------------------------------

# Variables may be set from the command line
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Ensure sphinx-build is available
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have\
 Sphinx installed, then set the SPHINXBUILD environment variable to\
 point to the full path of the '$(SPHINXBUILD)' executable.\
 Alternatively you can add the directory with the executable to your\
 PATH. If you don't have Sphinx installed, grab it from\
 http://sphinx-doc.org/)
endif

.PHONY: all
all:
	@$(error Please specify at least one target)


.PHONY: html
html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: html-release
html-release: clean
	SPHINX_HTML_BUILD_FOR_RELEASE=1 $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"
	rm -rf $(BUILDDIR)/doctrees $(BUILDDIR)/html/_sources
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."


.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*
