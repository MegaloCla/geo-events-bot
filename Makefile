# Inspired by: https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html

PYMODULE := geo_events
TESTS := tests
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)

.DEFAULT_GOAL := help

.PHONY: all
all: install lint tests

.PHONY: help
help:
	@echo "Please use 'make <target>', where <target> is one of"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  lint        run the code linters"
	@echo "  tests       run all the tests"
	@echo "  all         install, lint, and test the project"
	@echo "  build       build the package"
	@echo "  clean       remove all temporary files listed in .gitignore"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."
	@echo "Most actions are configured in 'pyproject.toml'."

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install --with dev,test
	touch $(INSTALL_STAMP)

.PHONY: lint
lint: $(INSTALL_STAMP)
    # Configured in pyproject.toml
    # Skips mypy if not installed
    #
    # $(POETRY) run black --check $(TESTS) $(PYMODULE) --diff
	@echo "Running Mypy...";
	$(POETRY) run mypy src/;
	@echo "Running Ruff...";
	$(POETRY) run ruff check --fix --config=pyproject.toml
	$(POETRY) run ruff format --config=pyproject.toml

.PHONY: tests
tests: $(INSTALL_STAMP)
    # Configured in pyproject.toml
	$(POETRY) run pytest $(TESTS)

.PHONY: build
build: lint tests
	$(POETRY) build

.PHONY: clean
clean:
    # Delete all files in .gitignore
	git clean -Xdf
