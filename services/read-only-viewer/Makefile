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

help:
	@echo "Read-Only Viewer Service Targets:"
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
