# DoS UI Service Makefile
# This service provides the main user interface for the Directory of Services

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= dos-ui
DEPLOYMENT_WORKSPACE := $(if $(WORKSPACE),-$(WORKSPACE))

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
install-dependencies: ## Install all dependencies
	asdf install
	npm i -g npm@latest
	npm install
