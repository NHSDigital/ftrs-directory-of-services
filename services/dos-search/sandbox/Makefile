BUILD_MAKEFILE := $(abspath $(lastword $(MAKEFILE_LIST)))
DOCKER_CONTEXT := $(realpath $(dir $(BUILD_MAKEFILE)))
ROOT_DIR_DEFAULT := $(realpath $(DOCKER_CONTEXT)/../../..)
ROOT_DIR ?= $(ROOT_DIR_DEFAULT)

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

.DEFAULT_GOAL := build

.PHONY: help clean install install-dependencies docker-install build unit-test push publish print-proxygen-config

SERVICE ?= dos-search-sandbox
AWS_REGION ?= eu-west-2
PROXYGEN_API_NAME ?= dos-search
PROXYGEN_ENV ?= internal-dev-sandbox
PROXYGEN_TOKEN_SCRIPT ?= ../../../scripts/workflow/get-apim-token.sh
PUSH_SCRIPT ?= ./push.sh
PUBLISH_SCRIPT ?= ./publish.sh
COMMIT_HASH ?= $(shell git -C $(ROOT_DIR) rev-parse --short HEAD 2>/dev/null)
REQUIRED_BINARIES ?= docker jq curl
BUILD_DIR := ../../build/services/${SERVICE}
IMAGE_REPOSITORY ?= ${ECR_REGISTRY}
IMAGE_NAME ?= $(or ${IMAGE_OVERRIDE},sandbox-dos-search)
IMAGE_TAG ?= $(or ${COMMIT_HASH},$(or ${APPLICATION_TAG},latest))
FULL_IMAGE := $(if ${IMAGE_REPOSITORY},${IMAGE_REPOSITORY}/${IMAGE_NAME},${IMAGE_NAME}):${IMAGE_TAG}
CONTAINER_NAME := ${SERVICE}-tests
SMOKE_SCRIPT := ./scripts/smoke.sh

# Emit Proxygen configuration in KEY=VALUE form for CI to consume
.PHONY: print-proxygen-config
print-proxygen-config:
	@echo "PROXYGEN_API_NAME=${PROXYGEN_API_NAME}"
	@echo "PROXYGEN_ENV=${PROXYGEN_ENV}"
	@echo "AWS_REGION=${AWS_REGION}"
	@echo "PROXYGEN_SPEC_PATH=${PROXYGEN_SPEC_PATH}"

clean:
	rm -rf $(BUILD_DIR)
	docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true
	docker images --format '{{.Repository}}:{{.Tag}}' | grep -E "^${IMAGE_REPOSITORY}/${IMAGE_NAME}" | xargs -r docker rmi

install: install-dependencies docker-install

install-dependencies:
	$(MAKE) -C $(ROOT_DIR) _install-dependencies

docker-install:
	if ! command -v docker >/dev/null 2>&1; then \
		if command -v apt-get >/dev/null 2>&1; then \
			sudo apt-get update; \
			sudo apt-get install -y docker.io; \
			sudo systemctl enable --now docker || true; \
			sudo usermod -aG docker $$USER || true; \
		else \
			echo "Docker CLI not found and cannot be installed automatically on this platform"; \
			exit 1; \
		fi; \
	fi
	docker version

build:
	docker build --platform linux/amd64 -t ${FULL_IMAGE} ${DOCKER_CONTEXT}
	echo "Built image ${FULL_IMAGE}"

unit-test:
	docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true
	docker run -d --rm -p 9000:9000 --name ${CONTAINER_NAME} ${FULL_IMAGE}
	@trap 'docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true' EXIT TERM INT; \
	WAIT_SECS=60 BASE_URL=http://localhost:9000 ${SMOKE_SCRIPT}

push:
	if [ -z "${PROXYGEN_API_NAME}" ]; then \
		echo "Missing required environment variable: PROXYGEN_API_NAME"; \
		exit 1; \
	fi
	if ! docker image inspect ${FULL_IMAGE} >/dev/null 2>&1; then \
		echo "Docker image ${FULL_IMAGE} not found; run 'make build' first"; \
		exit 1; \
	fi
	if [ -z "${IMAGE_NAME}" ]; then \
		echo "IMAGE_NAME is required"; \
		exit 1; \
	fi
	if [ -z "${IMAGE_TAG}" ]; then \
		echo "IMAGE_TAG is required"; \
		exit 1; \
	fi
	TOKEN="${PROXYGEN_ACCESS_TOKEN}"
	if [ -z "$$TOKEN" ]; then \
		if [ -z "${PROXYGEN_ENV}" ]; then \
			echo "Set PROXYGEN_ENV or provide PROXYGEN_ACCESS_TOKEN"; \
			exit 1; \
		fi; \
		SCRIPT_PATH="${PROXYGEN_TOKEN_SCRIPT}"; \
		if [ ! -f "$$SCRIPT_PATH" ]; then \
			echo "Token script $$SCRIPT_PATH not found"; \
			exit 1; \
		fi; \
		chmod +x "$$SCRIPT_PATH" >/dev/null 2>&1 || true; \
		TOKEN=$$(ENV=${PROXYGEN_ENV} API_NAME=${PROXYGEN_API_NAME} AWS_REGION=${AWS_REGION} "$$SCRIPT_PATH"); \
	fi
	if [ -z "$$TOKEN" ]; then \
		echo "Failed to obtain Proxygen access token"; \
		exit 1; \
	fi
	if [ ! -f "${PUSH_SCRIPT}" ]; then \
		echo "Push script not found: ${PUSH_SCRIPT}"; \
		exit 1; \
	fi
	chmod +x "${PUSH_SCRIPT}" >/dev/null 2>&1 || true
	ACCESS_TOKEN="$$TOKEN" "${PUSH_SCRIPT}" "${PROXYGEN_API_NAME}" "${FULL_IMAGE}" "${IMAGE_NAME}" "${IMAGE_TAG}"

publish:
	if [ -z "${PROXYGEN_API_NAME}" ]; then \
		echo "Missing required environment variable: PROXYGEN_API_NAME"; \
		exit 1; \
	fi
	if [ -z "${PROXYGEN_SPEC_PATH}" ]; then \
		echo "Missing required environment variable: PROXYGEN_SPEC_PATH"; \
		exit 1; \
	fi
	if [ ! -f "${PROXYGEN_SPEC_PATH}" ]; then \
		echo "Specification file not found: ${PROXYGEN_SPEC_PATH}"; \
		exit 1; \
	fi
	DEPLOY_TOKEN="${PROXYGEN_ACCESS_TOKEN}"
	if [ -z "$$DEPLOY_TOKEN" ]; then \
		if [ -z "${PROXYGEN_ENV}" ]; then \
			echo "Set PROXYGEN_ENV or provide PROXYGEN_ACCESS_TOKEN"; \
			exit 1; \
		fi; \
		SCRIPT_PATH="${PROXYGEN_TOKEN_SCRIPT}"; \
		if [ ! -f "$$SCRIPT_PATH" ]; then \
			echo "Token script $$SCRIPT_PATH not found"; \
			exit 1; \
		fi; \
		chmod +x "$$SCRIPT_PATH" >/dev/null 2>&1 || true; \
		DEPLOY_TOKEN=$$(ENV=${PROXYGEN_ENV} API_NAME=${PROXYGEN_API_NAME} AWS_REGION=${AWS_REGION} "$$SCRIPT_PATH"); \
	fi
	if [ -z "$$DEPLOY_TOKEN" ]; then \
		echo "Failed to obtain Proxygen deploy token"; \
		exit 1; \
	fi
	if [ ! -f "${PUBLISH_SCRIPT}" ]; then \
		echo "Publish script not found: ${PUBLISH_SCRIPT}"; \
		exit 1; \
	fi
	chmod +x "${PUBLISH_SCRIPT}" >/dev/null 2>&1 || true
	ACCESS_TOKEN="$$DEPLOY_TOKEN" "${PUBLISH_SCRIPT}" "${PROXYGEN_ENV}" "${PROXYGEN_API_NAME}" "${PROXYGEN_SPEC_PATH}"
