
.DEFAULT_GOAL := test-unit
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

clean-pyc: ## Clean Python temporary files
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build: ## Clean Python build directories
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

clean: clean-pyc clean-build ## Clean all Python auto-generated files and virtual environments
	rm --force --recursive devenv
	rm --force --recursive .mytox

devenv: ## Build a Python virtual environment
	tox -e devenv

test: ## Run the unit test suite
	tox

test-unit: ## Run the unit tests using the current virtual environment
	. devenv/bin/activate && py.test -svk unit

run: ## Run a development server using Gunicorn
	. devenv/bin/activate && gunicorn -t 1000 -b 0.0.0.0:8080 kiln_share:app --reload
