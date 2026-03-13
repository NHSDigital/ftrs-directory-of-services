# Slack Notifier Service Makefile
# This service provides Slack notification functionality for CloudWatch alarms

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= slack-notifier
PROJECT_VERSION := $(shell grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
WHEEL_NAME := slack_notifier-$(PROJECT_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk
