# Read-Only Viewer Service Makefile
# This service provides a read-only view of the Directory of Services data

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= read-only-viewer

# Deployment bucket configuration
DEPLOYMENT_BUCKET ?= ftrs-dos-$(ENVIRONMENT)-$(SERVICE)-frontend-bucket$(DEPLOYMENT_WORKSPACE)
READ_ONLY_VIEWER_DOMAIN_NAME = $(DEPLOYMENT_BUCKET).s3.$(AWS_REGION).amazonaws.com
CLOUDFRONT_DISTRIBUTION_ID := $(shell aws cloudfront list-distributions \
	--query "DistributionList.Items[?contains(Origins.Items[*].DomainName, '$(READ_ONLY_VIEWER_DOMAIN_NAME)')].Id" \
	--output text)

# ==============================================================================
# Include Shared Node Service Targets
# ==============================================================================

include ../../scripts/services/node-service.mk

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  Read Only Viewer Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
