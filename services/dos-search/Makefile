# DoS Search Service Makefile
# This service provides search functionality for the Directory of Services

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= dos-search
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := dos_search-$(POETRY_VERSION)-py3-none-any.whl
LAMBDA_SOURCES_SUBDIR := src
LAMBDA_SUBDIRS := organization healthcare_service health_check

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Overrides
# ==============================================================================

_install-dependency: ## Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf plugin update ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: ## Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done
