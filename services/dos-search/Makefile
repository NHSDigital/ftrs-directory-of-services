# DoS Search Service Makefile
# This service provides search functionality for the Directory of Services

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= dos-search
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := dos_search-$(POETRY_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Overrides
# ==============================================================================

# Override dependency layer export to exclude additional groups
build-dependency-layer: clean
	@echo "Building dependency layer for $(SERVICE)..."
	@mkdir -p $(DEPENDENCY_DIR)/python
	poetry export --without dev --without test --without shared --without-hashes > $(DEPENDENCY_DIR)/requirements.txt
	pip install \
		--platform $(PLATFORM) \
		--target $(DEPENDENCY_DIR)/python \
		--implementation cp \
		--python-version $(PYTHON_VERSION) \
		--no-deps \
		--upgrade \
		-r $(DEPENDENCY_DIR)/requirements.txt
	cd $(DEPENDENCY_DIR) && zip -r -q ../$(DEPENDENCY_LAYER_NAME).zip * --exclude "*__pycache__/*"
	@echo "Dependency layer built: $(DEPENDENCY_LAYER_NAME).zip"

_install-dependency: # Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf plugin update ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: # Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "DoS Search Service Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install              - Install dependencies"
	@echo "  make lint                 - Run linting checks"
	@echo "  make lint-fix             - Fix linting issues"
	@echo "  make test                 - Run tests"
	@echo "  make build                - Build Lambda package"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish              - Publish to development"
	@echo "  make stage-release        - Stage release"
	@echo "  make promote-rc           - Promote to RC"
	@echo "  make publish-release      - Publish release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                - Clean build artifacts"
