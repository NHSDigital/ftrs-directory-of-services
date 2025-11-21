BUILD_MAKEFILE := $(abspath $(lastword $(MAKEFILE_LIST)))
DOCKER_CONTEXT := $(realpath $(dir $(BUILD_MAKEFILE)))
ROOT_DIR_DEFAULT := $(realpath $(DOCKER_CONTEXT)/../../)
ROOT_DIR ?= $(ROOT_DIR_DEFAULT)

ARTIFACT_NAME := $(notdir $(realpath $(DOCKER_CONTEXT)))
BUILD_OUTPUT_DIR := $(ROOT_DIR)/build/services/$(ARTIFACT_NAME)

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

.DEFAULT_GOAL := build

.PHONY: install build unit-test push publish lint

API_NAME ?= dos-search
PUSH_SCRIPT ?= $(ROOT_DIR)/scripts/workflow/push-to-ecr.sh
GET_APIM_TOKEN_SCRIPT ?= $(ROOT_DIR)/scripts/workflow/get-apim-token.sh

ENVIRONMENT ?=
AWS_REGION ?=
# Compute a canonical secret environment value inside make (prefer ENV, then ENVIRONMENT, otherwise 'mgmt')
SECRET_ENV_MAKE := $(if $(ENV),$(ENV),$(if $(ENVIRONMENT),$(ENVIRONMENT),mgmt))

ifneq ($(strip $(COMMIT_HASH)),)
COMMIT_SOURCE := $(strip $(COMMIT_HASH))
else
ifneq ($(strip $(GITHUB_SHA)),)
COMMIT_SOURCE := $(shell printf '%.7s' "$(GITHUB_SHA)")
else
COMMIT_SOURCE := $(shell git -C $(ROOT_DIR) rev-parse --short HEAD 2>/dev/null || true)
endif
endif

IMAGE_TAG ?= $(if $(COMMIT_SOURCE),$(COMMIT_SOURCE),latest)
COMMIT_HASH ?= $(IMAGE_TAG)
FULL_IMAGE := ${API_NAME}:${IMAGE_TAG}
CONTAINER_NAME := ${API_NAME}-tests
SMOKE_SCRIPT := ./scripts/smoke.sh

install:
	if command -v docker >/dev/null 2>&1; then \
		echo "Docker already installed"; \
		docker version; \
		exit 0; \
	fi
	DISTRO_CODENAME=$$(. /etc/os-release && echo $$VERSION_CODENAME); \
	ARCH=$$(dpkg --print-architecture); \
	sudo install -m 0755 -d /etc/apt/keyrings; \
	sudo rm -f /etc/apt/keyrings/docker.gpg; \
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; \
	echo "deb [arch=$$ARCH signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $$DISTRO_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null; \
	sudo apt-get update; \
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	docker version

build:
	docker build --platform linux/amd64 -t ${FULL_IMAGE} ${DOCKER_CONTEXT}
	echo "Built image ${FULL_IMAGE}"

	mkdir -p "$(BUILD_OUTPUT_DIR)"

	IMAGE_ID=$$(docker image inspect -f '{{.Id}}' "${FULL_IMAGE}" 2>/dev/null || echo "")
	REPO_DIGEST=$$(docker image inspect -f '{{index .RepoDigests 0}}' "${FULL_IMAGE}" 2>/dev/null || echo "")
	BUILT_AT=$$(date -u +"%Y-%m-%dT%H:%M:%SZ")

	printf '{"image":"%s","image_id":"%s","repo_digest":"%s","built_at":"%s"}\n' "${FULL_IMAGE}" "$${IMAGE_ID:-}" "$${REPO_DIGEST:-}" "$${BUILT_AT:-}" > "$(BUILD_OUTPUT_DIR)/manifest.json.tmp" && \
	mv "$(BUILD_OUTPUT_DIR)/manifest.json.tmp" "$(BUILD_OUTPUT_DIR)/manifest.json"

	tar --exclude="build" --exclude=".git" --exclude=".venv" --exclude="venv" --exclude="node_modules" -czf "$(BUILD_OUTPUT_DIR)/source.tar.gz" -C "${DOCKER_CONTEXT}" . || true

unit-test: build
	docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true
	docker run -d --rm -p 9000:9000 --name ${CONTAINER_NAME} ${FULL_IMAGE}
	@trap 'docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true' EXIT TERM INT; \
	WAIT_SECS=60 BASE_URL=http://localhost:9000 ${SMOKE_SCRIPT}

publish:
	@echo "Skipping S3 artefact publish for sandbox service"

push-to-ecr:
	@echo "Running pre-push diagnostics..."
	@$(MAKE) diagnose

	if [ -z "${API_NAME}" ]; then \
		echo "Missing required variable: API_NAME"; \
		exit 1; \
	fi
	if ! docker image inspect ${FULL_IMAGE} >/dev/null 2>&1; then \
		echo "Docker image ${FULL_IMAGE} not found; run 'make build' first"; \
		exit 1; \
	fi
	if [ -z "${IMAGE_TAG}" ]; then \
		echo "IMAGE_TAG is required"; \
		exit 1; \
	fi

	if [ ! -f "${PUSH_SCRIPT}" ]; then \
		echo "Push script not found: ${PUSH_SCRIPT}"; \
		exit 1; \
	fi
	chmod +x "${PUSH_SCRIPT}" >/dev/null 2>&1 || true
	python -m pip install --upgrade pip >/dev/null 2>&1 || true; \
	python -m pip install pyjwt cryptography >/dev/null 2>&1 || true; \
	if [ ! -f "$(GET_APIM_TOKEN_SCRIPT)" ]; then \
		echo "get-apim-token script not found: $(GET_APIM_TOKEN_SCRIPT)"; \
		exit 1; \
	fi; \
	chmod +x "$(GET_APIM_TOKEN_SCRIPT)" >/dev/null 2>&1 || true; \
	ACCESS_TOKEN="$$(API_NAME="${API_NAME}" ENV="$(ENVIRONMENT)" AWS_REGION="$(AWS_REGION)" /bin/bash "$(GET_APIM_TOKEN_SCRIPT)")"; \
	if [ -z "$$ACCESS_TOKEN" ]; then \
		echo "Failed to retrieve APIM access token"; \
		exit 1; \
	fi
	# If the desired commit (COMMIT_SOURCE) differs from IMAGE_TAG, retag the built image to COMMIT_SOURCE
	if [ -n "${COMMIT_SOURCE}" ] && [ "${COMMIT_SOURCE}" != "${IMAGE_TAG}" ]; then \
		echo "Retagging image ${FULL_IMAGE} -> ${API_NAME}:${COMMIT_SOURCE}"; \
		docker tag "${FULL_IMAGE}" "${API_NAME}:${COMMIT_SOURCE}"; \
		PUSH_IMAGE="${API_NAME}:${COMMIT_SOURCE}"; \
	else \
		PUSH_IMAGE="${FULL_IMAGE}"; \
	fi; \
	ACCESS_TOKEN="$$ACCESS_TOKEN" "${PUSH_SCRIPT}" "${API_NAME}" "${PUSH_IMAGE}" "${API_NAME}" "${IMAGE_TAG}"

lint:
	@echo "No lint step for sandbox service"

.PHONY: check-aws check-aws-cli check-aws-sts check-docker check-pushscript check-get-apim-token diagnose

# Check that AWS environment variables are present (non-fatal; sts check validates credentials)
check-aws:
	@echo "Checking AWS environment variables (non-fatal)..."; \
	if [ -n "$${AWS_ACCESS_KEY_ID:-}" ] && [ -n "$${AWS_SECRET_ACCESS_KEY:-}" ]; then \
		echo "OK: AWS credentials present in environment"; \
	else \
		echo "WARN: AWS env credentials not present; will verify via 'aws sts' check"; \
	fi; \
	if [ -n "$${AWS_REGION:-}" ] || [ -n "$${AWS_DEFAULT_REGION:-}" ]; then \
		echo "OK: AWS region set"; \
	else \
		echo "WARN: AWS region not set (AWS_REGION/AWS_DEFAULT_REGION)"; \
	fi

# Check aws CLI is available
check-aws-cli:
	@command -v aws >/dev/null 2>&1 && echo "OK: aws CLI found: $$(aws --version 2>&1 | head -n1)" || (echo "ERROR: aws CLI not found"; exit 1)

# Try calling STS to verify assumed credentials work
check-aws-sts:
	@echo "Verifying AWS caller identity..."; \
	aws sts get-caller-identity --output json >/dev/null 2>&1 && echo "OK: sts get-caller-identity succeeded" || (echo "ERROR: sts get-caller-identity failed (check credentials/role)"; exit 1)

# Check docker availability and daemon
check-docker:
	@command -v docker >/dev/null 2>&1 || (echo "ERROR: docker not installed"; exit 1); \
	docker info >/dev/null 2>&1 && echo "OK: docker is running" || (echo "ERROR: docker daemon not available or permission denied"; exit 1)

# Ensure push script exists and look for explicit AWS env forwarding in it
check-pushscript:
	@echo "Checking push script at $(PUSH_SCRIPT)"; \
	if [ -f "$(PUSH_SCRIPT)" ]; then echo "OK: push script exists"; else echo "ERROR: push script $(PUSH_SCRIPT) not found"; exit 1; fi; \
	# Look for docker -e or AWS env references inside script to warn if docker run might not get creds
	if grep -E "-e\s+AWS|AWS_ACCESS_KEY_ID|AWS_SESSION_TOKEN|AWS_SECRET_ACCESS_KEY|--env" "$(PUSH_SCRIPT)" >/dev/null 2>&1; then \
		echo "Note: push script forwards AWS envs or references AWS vars"; \
	else \
		echo "Note: push script does not explicitly forward AWS envs; if it runs docker containers ensure AWS vars are passed"; \
	fi

# Attempt to retrieve APIM token using the token script (non-fatal if script not present)
check-get-apim-token:
	@echo "Attempting to fetch APIM token via $(GET_APIM_TOKEN_SCRIPT)"; \
	if [ ! -f "$(GET_APIM_TOKEN_SCRIPT)" ]; then echo "WARN: $(GET_APIM_TOKEN_SCRIPT) not found; skipping APIM token check"; exit 0; fi; \
	chmod +x "$(GET_APIM_TOKEN_SCRIPT)" >/dev/null 2>&1 || true; \
	# Ensure python deps for token script are available for diagnostics
	python -m pip install --upgrade pip >/dev/null 2>&1 || true; \
	python -m pip install pyjwt cryptography >/dev/null 2>&1 || true; \
	# Explicit one-step Secrets Manager read test (shows JSON on success or prints exit code on failure)
	echo "Running explicit secret read test:"; \
	aws secretsmanager get-secret-value --secret-id "/ftrs-dos/$(SECRET_ENV_MAKE)/$(API_NAME)-proxygen-jwt-credentials" --region "${AWS_REGION:-eu-west-2}" --output json || echo "SECRET READ FAILED: $$?"; \
	# Use make-expanded secret path directly to avoid shell unbound-variable issues
	echo "Secret id to fetch: /ftrs-dos/$(SECRET_ENV_MAKE)/$(API_NAME)-proxygen-jwt-credentials"; \
	# Try to fetch the raw secret to surface permission or not-found errors
	aws secretsmanager get-secret-value --secret-id "/ftrs-dos/$(SECRET_ENV_MAKE)/$(API_NAME)-proxygen-jwt-credentials" --region "$${AWS_REGION:-}" --output text >/dev/null 2>&1 || echo "WARN: unable to read secret /ftrs-dos/$(SECRET_ENV_MAKE)/$(API_NAME)-proxygen-jwt-credentials (check permissions/exists)"; \
	# Run token script and let stderr surface for debugging (pass expanded API_NAME and the make-computed ENV)
	ACCESS_TOKEN="$$(API_NAME="$(API_NAME)" ENV="$(SECRET_ENV_MAKE)" AWS_REGION="$${AWS_REGION:-}" /bin/bash "$(GET_APIM_TOKEN_SCRIPT)" 2>&1 || true)"; \
	# If script produced JSON or token on stdout, try to extract token from output
	# Use parameter expansion so the shell doesn't error under set -u when ACCESS_TOKEN is empty
	if echo "$${ACCESS_TOKEN:-}" | grep -q 'Error:'; then \
		echo "Token script error output:"; \
		echo "$${ACCESS_TOKEN:-}"; \
		exit 1; \
	fi; \
	if [ -n "$${ACCESS_TOKEN:-}" ]; then echo "OK: Retrieved APIM token (len=$$(echo -n "$${ACCESS_TOKEN:-}" | wc -c))"; else echo "ERROR: Failed to retrieve APIM token (empty)"; exit 1; fi

# Aggregate diagnostics
diagnose: check-aws check-aws-cli check-aws-sts check-docker check-pushscript check-get-apim-token
	@echo "All diagnostics complete"
