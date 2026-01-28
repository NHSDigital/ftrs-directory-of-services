# Shared Makefile for Node.js-based services (Frontend applications)
# Include this in service Makefiles with: include ../../scripts/services/node-service.mk

# ==============================================================================
# Common Variables
# ==============================================================================

BUILD_DIR := ../../build/services/$(SERVICE)
ARTEFACT_BUCKET := $(REPO_NAME)-mgmt-artefacts-bucket
TEMP_DIRECTORY ?= ./temp
BUILD_TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),null)
BUILD_INFO_FILE := $(BUILD_DIR)/build-info.json

COLOR_ORANGE := \033[0;33m
COLOR_GREEN := \033[0;32m
COLOR_RESET := \033[0m

define log_start
	@echo "$(COLOR_ORANGE)$(1)...$(COLOR_RESET)"
endef

define log_success
	@echo "$(COLOR_GREEN)✓ $(1)$(COLOR_RESET)"
endef

# ------------------------------------------------------------------------------
# Development artefact path (branch-aware)
# ------------------------------------------------------------------------------

DEPLOYMENT_WORKSPACE := $(if $(WORKSPACE),$(if $(filter default,$(WORKSPACE)),,-$(WORKSPACE)),)

BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/latest
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/$(WORKSPACE)
endif

# ------------------------------------------------------------------------------
# Promotion paths
# ------------------------------------------------------------------------------

ARTEFACT_STAGING_PATH = $(ARTEFACT_BUCKET)/staging/$(PRERELEASE_TAG)
ARTEFACT_RELEASE_CANDIDATE_PATH = $(ARTEFACT_BUCKET)/release-candidates/$(RELEASE_TAG)

# ------------------------------------------------------------------------------
# Resolve artefact source path (used by deploy)
# Priority: release → prerelease → development
# ------------------------------------------------------------------------------

ifeq ($(strip $(RELEASE_TAG)),)
	ARTEFACT_SOURCE_PATH = $(ARTEFACT_DEVELOPMENT_PATH)
else
	ARTEFACT_SOURCE_PATH = $(ARTEFACT_RELEASE_CANDIDATE_PATH)
endif

# ==============================================================================
# Common Targets
# ==============================================================================

.PHONY: ensure-build-dir clean install install-dependencies format lint \
		unit-test generate-build-info build publish deploy \
		invalidate-cloudfront-cache stage-release promote-rc publish-release

ensure-build-dir:
	@mkdir -p $(BUILD_DIR)

clean: ## Clean build artifacts and caches
	@rm -rf .eslintcache .jest .tmp .coverage coverage.xml .vinxi .output
	@rm -rf $(BUILD_DIR)

install: install-dependencies ## Install project dependencies

install-dependencies:
	asdf install
	npm install

format:
	npm run format -- --fix
	npm run lint -- --fix

lint: ## Run linting checks
	npm run check
	npm run build:types -- --noEmit

unit-test: ## Run unit tests
	npm run test

generate-build-info: ensure-build-dir
	@echo '{' > $(BUILD_INFO_FILE)
	@echo '  "git_commit": "$(COMMIT_HASH)",' >> $(BUILD_INFO_FILE)
	@echo '  "build_timestamp": "$(BUILD_TIMESTAMP)",' >> $(BUILD_INFO_FILE)
	@echo '  "release_version": "$(RELEASE_VERSION)"' >> $(BUILD_INFO_FILE)
	@echo '}' >> $(BUILD_INFO_FILE)

build: clean ensure-build-dir generate-build-info ### Build the service
	$(call log_start,Building $(SERVICE))
	npm run build
	cd .output/public && zip -r -q ../../$(BUILD_DIR)/$(SERVICE)-assets.zip *
	cd .output/server && zip -r -q ../../$(BUILD_DIR)/$(SERVICE)-server.zip *
	$(call log_success,Build complete: $(SERVICE)-assets.zip, $(SERVICE)-server.zip)

# ------------------------------------------------------------------------------
# Publish (development)
# ------------------------------------------------------------------------------

publish: ## Publish artifacts to S3 development path
	$(call log_start,Publishing $(SERVICE) to $(ARTEFACT_DEVELOPMENT_PATH)...)
	aws s3 sync $(BUILD_DIR)/ s3://$(ARTEFACT_DEVELOPMENT_PATH)/ --region $(AWS_REGION)
	$(call log_success,Published successfully)

# ------------------------------------------------------------------------------
# Deploy (dev / staging / release-candidates / release)
# ------------------------------------------------------------------------------

deploy: ## Deploy artifacts from S3 to deployment bucket
	$(call log_start,Deploying $(SERVICE) from $(ARTEFACT_SOURCE_PATH)...)
	aws s3 cp s3://$(ARTEFACT_SOURCE_PATH)/$(SERVICE)-assets.zip .
	unzip -q $(SERVICE)-assets.zip -d $(TEMP_DIRECTORY)
	aws s3 sync --delete $(TEMP_DIRECTORY)/ s3://$(DEPLOYMENT_BUCKET)/
	rm -rf $(TEMP_DIRECTORY) $(SERVICE)-assets.zip

# ------------------------------------------------------------------------------
# CloudFront
# ------------------------------------------------------------------------------

invalidate-cloudfront-cache: ## Invalidate CloudFront cache
	$(call log_start,Invalidating CloudFront cache for distribution: $(CLOUDFRONT_DISTRIBUTION_ID))
	@if [ -z "$(CLOUDFRONT_DISTRIBUTION_ID)" ]; then \
		echo "ERROR: CLOUDFRONT_DISTRIBUTION_ID not set"; \
		exit 1; \
	fi
	aws cloudfront create-invalidation --distribution-id $(CLOUDFRONT_DISTRIBUTION_ID) --paths "/*"
	$(call log_success,Cache invalidation initiated)

pre-commit: lint

# ==============================================================================
# Help Target
# ==============================================================================

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  $(SERVICE) Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
