# Shared Makefile for artefact promotion of services

.PHONY: stage release-candidate release

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),$(if $(PRERELEASE_TAG),$(PRERELEASE_TAG),null))
RETAIN_VERSIONS ?= 5
TAG_CONCURRENCY ?= 10

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

# Full-reconciliation retention tagging for a versioned S3 prefix.
# Iterates all versions each run to ensure the full retain window is correct,
# regardless of RETAIN_VERSIONS changes, manual tag edits, or prior partial failures.
# Per-key tagging is parallelised with bounded concurrency and PID tracking.
# Concurrency pool is global across all versions to maximise throughput.
# put-object-tagging is idempotent so no pre-read check is needed.
# $(1) = S3 prefix under bucket (e.g. staging, release-candidates)
# $(2) = current version tag (e.g. PRERELEASE_TAG or RELEASE_TAG)
define update-retention-tags
	@echo "Updating retention tags for $(1) (keep last $(RETAIN_VERSIONS) versions)..."; \
	all_versions=$$(aws s3 ls s3://$(ARTEFACT_BUCKET)/$(1)/ --region $(AWS_REGION) | awk '{print $$2}' | sed 's/\/$$//' | sort -V); \
	retain_versions=$$(echo "$$all_versions" | tail -$(RETAIN_VERSIONS)); \
	pids=""; failed=0; count=0; \
	for version in $$all_versions; do \
		if echo "$$retain_versions" | grep -qx "$$version"; then \
			retention_value=retain; \
		else \
			retention_value=ephemeral; \
		fi; \
		keys=$$(aws s3api list-objects-v2 --bucket $(ARTEFACT_BUCKET) --prefix "$(1)/$$version/" --query 'Contents[].Key' --output text --region $(AWS_REGION)); \
		if [ -z "$$keys" ] || [ "$$keys" = "None" ]; then \
			echo "No objects found under $(1)/$$version - skipping"; \
			continue; \
		fi; \
		for key in $$keys; do \
			aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$key" --tagging "TagSet=[{Key=retention,Value=$$retention_value}]" --region $(AWS_REGION) & \
			pids="$$pids $$!"; \
			count=$$((count + 1)); \
			if [ $$((count % $(TAG_CONCURRENCY))) -eq 0 ]; then \
				for pid in $$pids; do wait $$pid || failed=1; done; \
				pids=""; \
			fi; \
		done; \
	done; \
	for pid in $$pids; do wait $$pid || failed=1; done; \
	if [ $$failed -ne 0 ]; then \
		echo "$(COLOR_RED)ERROR: One or more tagging operations failed$(COLOR_RESET)"; \
		exit 1; \
	fi
endef

stage:
	@[ -n "$(PRERELEASE_TAG)" ] || (echo "$(COLOR_RED)ERROR: PRERELEASE_TAG is not set; cannot stage artefacts$(COLOR_RESET)" && exit 1)
	$(call log_start,Staging release $(PRERELEASE_TAG))
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/ s3://$(ARTEFACT_STAGING_PATH)/ --recursive --region $(AWS_REGION)
	$(call update-retention-tags,staging,$(PRERELEASE_TAG))
	$(call log_success,Release staged successfully)

release-candidate:
	@[ -n "$(PRERELEASE_TAG)" ] || (echo "$(COLOR_RED)ERROR: PRERELEASE_TAG is not set; cannot promote release-candidate artefacts$(COLOR_RESET)" && exit 1)
	@[ -n "$(RELEASE_TAG)" ] || (echo "$(COLOR_RED)ERROR: RELEASE_TAG is not set; cannot promote release-candidate artefacts$(COLOR_RESET)" && exit 1)
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
	if [ -z "$$keys" ] || [ "$$keys" = "None" ]; then \
		echo "No objects found under releases/$(RELEASE_VERSION_CLEAN) - skipping tagging"; \
	else \
	pids=""; failed=0; count=0; \
	for key in $$keys; do \
		aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$$key" --tagging "TagSet=[{Key=retention,Value=permanent}]" --region $(AWS_REGION) & \
		pids="$$pids $$!"; \
		count=$$((count + 1)); \
		if [ $$((count % $(TAG_CONCURRENCY))) -eq 0 ]; then \
			for pid in $$pids; do wait $$pid || failed=1; done; \
			pids=""; \
		fi; \
	done; \
	for pid in $$pids; do wait $$pid || failed=1; done; \
	if [ $$failed -ne 0 ]; then \
		echo "$(COLOR_RED)ERROR: One or more tagging operations failed$(COLOR_RESET)"; \
		exit 1; \
	fi; \
	fi
	$(call log_success,Release published successfully to releases/$(RELEASE_VERSION_CLEAN))