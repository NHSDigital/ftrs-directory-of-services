# Slack Notifier Service Makefile
# This service provides Slack notification functionality for CloudWatch alarms

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= slack-notifier
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := slack_notifier-$(POETRY_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk
