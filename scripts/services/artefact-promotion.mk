# Shared Makefile for artefact promotion of services

.PHONY: set-prerelease-version stage-release promote-rc publish-release

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),$(if $(PRERELEASE_TAG),$(PRERELEASE_TAG),null))

BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/latest
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/$(WORKSPACE)
endif

ARTEFACT_STAGING_PATH = $(ARTEFACT_BUCKET)/staging/$(PRERELEASE_TAG)
ARTEFACT_RELEASE_CANDIDATE_PATH = $(ARTEFACT_BUCKET)/release-candidates/$(RELEASE_TAG)

COLOR_ORANGE := \033[0;33m
COLOR_GREEN := \033[0;32m
COLOR_RED := \033[0;31m
COLOR_RESET := \033[0m

define log_start
	@echo "$(COLOR_ORANGE)$(1)...$(COLOR_RESET)"
endef

define log_success
	@echo "$(COLOR_GREEN)✓ $(1)$(COLOR_RESET)"
endef

define update-build-info
	tmp_dir=$$(mktemp -d); \
	aws s3 cp s3://$(1)/build-info.json $$tmp_dir/build-info.json --region $(AWS_REGION); \
	jq '.release_version = "$(2)"' $$tmp_dir/build-info.json > $$tmp_dir/build-info.updated.json; \
	aws s3 cp $$tmp_dir/build-info.updated.json s3://$(1)/build-info.json --region $(AWS_REGION); \
	rm -rf $$tmp_dir
endef

set-prerelease-version:
ifeq ($(strip $(PRERELEASE_TAG)),)
	$(call log_start,Finding latest prerelease version)
	$(eval PRERELEASE_TAG := $(shell \
		aws s3 ls s3://$(ARTEFACT_BUCKET)/staging/ --region $(AWS_REGION) \
		| awk '{print $$2}' \
		| sed 's/\/$$//' \
		| sort -V \
		| tail -1 \
	))
	@if [ -z "$(PRERELEASE_TAG)" ]; then \
        echo "$(COLOR_RED)✗ ERROR: No prerelease versions found in staging$(COLOR_RESET)"; \
		exit 1; \
	fi
	$(call log_success,Using prerelease version: $(PRERELEASE_TAG))
else
	$(call log_success,Using provided prerelease version: $(PRERELEASE_TAG))
endif

stage: set-prerelease-version
	$(call log_start,Staging release $(PRERELEASE_TAG))
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/ s3://$(ARTEFACT_STAGING_PATH)/ --recursive --region $(AWS_REGION)
	$(call log_success,Release staged successfully)

release-candidate: set-prerelease-version
	$(call log_start,Promoting from staging/$(PRERELEASE_TAG) to release-candidates/$(RELEASE_TAG))
	aws s3 cp s3://$(ARTEFACT_STAGING_PATH)/ s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/ --recursive --region $(AWS_REGION)
	$(call update-build-info,$(ARTEFACT_RELEASE_CANDIDATE_PATH),$(RELEASE_TAG))
	$(call log_success,Promoted from staging/$(PRERELEASE_TAG) to release-candidates/$(RELEASE_TAG))

release:
	$(eval RELEASE_VERSION_CLEAN := $(shell echo "$(RELEASE_TAG)" | sed 's/-rc\.[0-9]*$$//'))
	$(eval ARTEFACT_RELEASE_PATH := $(ARTEFACT_BUCKET)/releases/$(RELEASE_VERSION_CLEAN))
	$(call log_start,Promoting from release-candidates/$(RELEASE_TAG) to releases/$(RELEASE_VERSION_CLEAN))
	aws s3 cp s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/ s3://$(ARTEFACT_RELEASE_PATH)/ --recursive --region $(AWS_REGION)
	$(call update-build-info,$(ARTEFACT_RELEASE_PATH),$(RELEASE_VERSION_CLEAN))
	$(call log_success,Release published successfully to releases/$(RELEASE_VERSION_CLEAN))