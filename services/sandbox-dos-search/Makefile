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
PUSH_SCRIPT ?= ./scripts/push.sh

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

push:
	if [ -z "${API_NAME}" ]; then \
		echo "Missing required environment variable: API_NAME"; \
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

	# Require PROXYGEN_ACCESS_TOKEN to be provided by the environment or caller
	TOKEN="$$PROXYGEN_ACCESS_TOKEN"; \
	if [ -z "$$TOKEN" ]; then \
		echo "Missing required environment variable: PROXYGEN_ACCESS_TOKEN"; \
		exit 1; \
	fi

	# token present

	if [ ! -f "${PUSH_SCRIPT}" ]; then \
		echo "Push script not found: ${PUSH_SCRIPT}"; \
		exit 1; \
	fi
	chmod +x "${PUSH_SCRIPT}" >/dev/null 2>&1 || true
	ACCESS_TOKEN="$$PROXYGEN_ACCESS_TOKEN" "${PUSH_SCRIPT}" "${API_NAME}" "${FULL_IMAGE}" "${API_NAME}" "${IMAGE_TAG}"

lint:
	@echo "No lint step for sandbox service"

