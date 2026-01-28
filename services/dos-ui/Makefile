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
install-dependencies: ## Install all dependencies
	asdf install
	npm i -g npm@latest
	npm install

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  DoS UI Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
