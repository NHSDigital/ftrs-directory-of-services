BUILD_MAKEFILE := $(abspath $(lastword $(MAKEFILE_LIST)))
DOCKER_CONTEXT := $(realpath $(dir $(BUILD_MAKEFILE)))
ROOT_DIR_DEFAULT := $(realpath $(DOCKER_CONTEXT)/../../..)
ROOT_DIR ?= $(ROOT_DIR_DEFAULT)

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

.DEFAULT_GOAL := build

SERVICE ?= dos-search-sandbox
AWS_REGION ?= eu-west-2
PROXYGEN_CLI ?= proxygen
PROXYGEN_API_NAME ?= dos-search_FHIR_R4
PROXYGEN_ENV ?= internal-dev-sandbox
PROXYGEN_TOKEN_SCRIPT ?= ../../../scripts/workflow/get-apim-token.sh
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

push: build
	if [ -z "${PROXYGEN_API_NAME}" ]; then \
		echo "Missing required environment variable: PROXYGEN_API_NAME"; \
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
	if ! command -v ${PROXYGEN_CLI} >/dev/null 2>&1; then \
		echo "${PROXYGEN_CLI} CLI not found on PATH"; \
		exit 1; \
	fi
	REGISTRY=$$(PROXYGEN_ACCESS_TOKEN="$$TOKEN" ${PROXYGEN_CLI} docker registry --api ${PROXYGEN_API_NAME})
	if [ -z "$$REGISTRY" ]; then \
		echo "Failed to resolve Proxygen docker registry"; \
		exit 1; \
	fi
	LOGIN_CMD=$$(PROXYGEN_ACCESS_TOKEN="$$TOKEN" ${PROXYGEN_CLI} docker get-login --api ${PROXYGEN_API_NAME})
	if [ -z "$$LOGIN_CMD" ]; then \
		echo "Failed to obtain Proxygen docker login token"; \
		exit 1; \
	fi
	docker login "$$LOGIN_CMD"
	REGISTRY_IMAGE_COMMIT=$${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
	REGISTRY_IMAGE_LATEST=$${REGISTRY}/${IMAGE_NAME}:latest
	docker tag ${FULL_IMAGE} $$REGISTRY_IMAGE_COMMIT
	docker push $$REGISTRY_IMAGE_COMMIT
	# Also update latest for stable spec consumption
	docker tag ${FULL_IMAGE} $$REGISTRY_IMAGE_LATEST
	docker push $$REGISTRY_IMAGE_LATEST

publish:
	if [ -z "${PROXYGEN_API_NAME}" ]; then \
		echo "Missing required environment variable: PROXYGEN_API_NAME"; \
		exit 1; \
	fi
	if [ ! -f "${PROXYGEN_SPEC_PATH}" ]; then \
		echo "Specification file not found: ${PROXYGEN_SPEC_PATH}"; \
		exit 1; \
	fi
	DEPLOY_TOKEN="${PROXYGEN_ACCESS_TOKEN}"
	if [ -z "$$DEPLOY_TOKEN" ]; then \
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
	if ! command -v ${PROXYGEN_CLI} >/dev/null 2>&1; then \
		echo "${PROXYGEN_CLI} CLI not found on PATH"; \
		exit 1; \
	fi
	PROXYGEN_ACCESS_TOKEN="$$DEPLOY_TOKEN" ${PROXYGEN_CLI} instance deploy ${PROXYGEN_ENV} ${PROXYGEN_API_NAME} "${PROXYGEN_SPEC_PATH}"
