# DoS UI Service Makefile
# This service provides the main user interface for the Directory of Services

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= dos-ui

# Deployment bucket configuration
DEPLOYMENT_BUCKET ?= ftrs-dos-$(ENVIRONMENT)-ui-frontend-bucket$(DEPLOYMENT_WORKSPACE)
UI_DOMAIN_NAME = $(DEPLOYMENT_BUCKET).s3.$(AWS_REGION).amazonaws.com
CLOUDFRONT_DISTRIBUTION_ID := $(shell aws cloudfront list-distributions \
	--query "DistributionList.Items[?contains(Origins.Items[*].DomainName, '$(UI_DOMAIN_NAME)')].Id" \
	--output text)

# ==============================================================================
# Include Shared Node Service Targets
# ==============================================================================

include ../../scripts/services/node-service.mk

# ==============================================================================
# Service-Specific Overrides
# ==============================================================================

# DoS UI uses npm@latest
install-dependencies:
	asdf install
	npm i -g npm@latest
	npm install

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "DoS UI Service Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install                      - Install dependencies"
	@echo "  make lint                         - Run linting checks"
	@echo "  make format                       - Format and fix code"
	@echo "  make unit-test                    - Run tests"
	@echo "  make build                        - Build application"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish                      - Publish to development"
	@echo "  make deploy                       - Deploy to S3 (ENVIRONMENT required)"
	@echo "  make invalidate-cloudfront-cache  - Invalidate CloudFront cache"
	@echo "  make stage-release                - Stage release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                        - Clean build artifacts"
	@echo ""
	@echo "Variables:"
	@echo "  ENVIRONMENT=$(ENVIRONMENT)"
	@echo "  DEPLOYMENT_BUCKET=$(DEPLOYMENT_BUCKET)"
