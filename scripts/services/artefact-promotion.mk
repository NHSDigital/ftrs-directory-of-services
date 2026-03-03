# Shared Makefile for artefact promotion of services

.PHONY: stage release-candidate release

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),$(if $(PRERELEASE_TAG),$(PRERELEASE_TAG),null))
RETAIN_VERSIONS ?= 5

# Determine branch: prefer GITHUB_REF_NAME (in CI), fallback to git command (local)
# In GitHub Actions detached HEAD state, git rev-parse returns "HEAD" not "main"
BRANCH ?= $(if $(GITHUB_REF_NAME),$(GITHUB_REF_NAME),$(shell git rev-parse --abbrev-ref HEAD))

ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/latest
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/$(WORKSPACE)
endif

ARTEFACT_STAGING_PATH = $(ARTEFACT_BUCKET)/staging/$(PRERELEASE_TAG)
ARTEFACT_RELEASE_CANDIDATE_PATH = $(ARTEFACT_BUCKET)/release-candidates/$(RELEASE_TAG)

RETENTION_TAG_EPHEMERAL := retention=ephemeral
RETENTION_TAG_RETAIN := retention=retain
RETENTION_TAG_RELEASE := retention=permanent

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
	key_prefix=$$(echo "$(1)" | sed 's|^$(ARTEFACT_BUCKET)/||'); \
	retention_value=$$(echo "$(3)" | sed 's/^retention=//'); \
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$key_prefix/build-info.json" --tagging "TagSet=[{Key=retention,Value=$$retention_value}]" --region $(AWS_REGION); \
	rm -rf $$tmp_dir
endef

# Incremental retention tagging for a versioned S3 prefix.
# Only processes 2 boundary versions per run (new version + evicted version).
# Skips entire evicted version if first object is already tagged ephemeral.
# Per-key tagging is parallelised with & / wait to minimise wall-clock time.
# $(1) = S3 prefix under bucket (e.g. staging, release-candidates)
# $(2) = current version tag (e.g. PRERELEASE_TAG or RELEASE_TAG)
define update-retention-tags
	@echo "Updating retention tags for $(1) (keep last $(RETAIN_VERSIONS) versions)..."; \
	all_versions=$$(aws s3 ls s3://$(ARTEFACT_BUCKET)/$(1)/ --region $(AWS_REGION) | awk '{print $$2}' | sed 's/\/$$//' | sort -V); \
	total=$$(echo "$$all_versions" | grep -c .); \
	if [ "$$total" -gt "$(RETAIN_VERSIONS)" ]; then \
		evicted=$$(echo "$$all_versions" | sed -n "$$(($$total - $(RETAIN_VERSIONS)))p"); \
		versions_to_process="$(2) $$evicted"; \
	else \
		versions_to_process="$(2)"; \
	fi; \
	retain_versions=$$(echo "$$all_versions" | tail -$(RETAIN_VERSIONS)); \
	for version in $$versions_to_process; do \
		if echo "$$retain_versions" | grep -qx "$$version"; then \
			retention_value=retain; \
		else \
			retention_value=ephemeral; \
		fi; \
		keys=$$(aws s3api list-objects-v2 --bucket $(ARTEFACT_BUCKET) --prefix "$(1)/$$version/" --query 'Contents[].Key' --output text --region $(AWS_REGION)); \
		if [ "$$retention_value" = "ephemeral" ]; then \
			first_key=$$(echo "$$keys" | awk '{print $$1}'); \
			if [ -n "$$first_key" ]; then \
				probe=$$(aws s3api get-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$first_key" --query "TagSet[?Key=='retention'].Value | [0]" --output text --region $(AWS_REGION) 2>/dev/null); \
				if [ "$$probe" = "ephemeral" ]; then \
					echo "Skipping $(1)/$$version (already ephemeral)"; \
					continue; \
				fi; \
			fi; \
		fi; \
		for key in $$keys; do \
			aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$key" --tagging "TagSet=[{Key=retention,Value=$$retention_value}]" --region $(AWS_REGION) & \
		done; \
		wait; \
	done
endef

stage:
	@[ -n "$(PRERELEASE_TAG)" ] || (echo "$(COLOR_RED)ERROR: PRERELEASE_TAG is not set; cannot stage artefacts$(COLOR_RESET)" && exit 1)
	$(call log_start,Staging release $(PRERELEASE_TAG))
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/ s3://$(ARTEFACT_STAGING_PATH)/ --recursive --region $(AWS_REGION)
	$(call update--tags,staging,$(PRERELEASE_TAG))
	$(call log_success,Release staged successfully)

release-candidate:
	$(call log_start,Promoting from staging/$(PRERELEASE_TAG) to release-candidates/$(RELEASE_TAG))
	aws s3 cp s3://$(ARTEFACT_STAGING_PATH)/ s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/ --recursive --region $(AWS_REGION)
	$(call update-build-info,$(ARTEFACT_RELEASE_CANDIDATE_PATH),$(RELEASE_TAG),$(RETENTION_TAG_EPHEMERAL))
	$(call update-retention-tags,release-candidates,$(RELEASE_TAG))
	$(call log_success,Promoted from staging/$(PRERELEASE_TAG) to release-candidates/$(RELEASE_TAG))

release:
	$(eval RELEASE_VERSION_CLEAN := $(shell echo "$(RELEASE_TAG)" | sed 's/-rc\.[0-9]*$$//'))
	$(eval ARTEFACT_RELEASE_PATH := $(ARTEFACT_BUCKET)/releases/$(RELEASE_VERSION_CLEAN))
	$(call log_start,Promoting from release-candidates/$(RELEASE_TAG) to releases/$(RELEASE_VERSION_CLEAN))
	aws s3 cp s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/ s3://$(ARTEFACT_RELEASE_PATH)/ --recursive --region $(AWS_REGION)
	$(call update-build-info,$(ARTEFACT_RELEASE_PATH),$(RELEASE_VERSION_CLEAN),$(RETENTION_TAG_RELEASE))
	@keys=$$(aws s3api list-objects-v2 --bucket $(ARTEFACT_BUCKET) --prefix "releases/$(RELEASE_VERSION_CLEAN)/" --query 'Contents[].Key' --output text --region $(AWS_REGION)); \
	for key in $$keys; do \
		aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$key" --tagging "TagSet=[{Key=retention,Value=permanent}]" --region $(AWS_REGION) & \
	done; \
	wait
	$(call log_success,Release published successfully to releases/$(RELEASE_VERSION_CLEAN))