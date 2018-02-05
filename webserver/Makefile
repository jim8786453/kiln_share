
.DEFAULT_GOAL := help
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

devenv: ## Build a Python virtual environment
	tox -e devenv

install: ## Install the full webserver locally
	. devenv/bin/activate && fab local install

run: ## Run the webserver locally
	. devenv/bin/activate && fab local start

build: ## Build the webserver locally
	. devenv/bin/activate && fab local configure_openresty restart
