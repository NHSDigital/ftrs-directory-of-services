# Data Migration Service Makefile
# This service handles data migration and ETL processes for the DoS platform

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= data-migration
WHEEL_NAME := pipeline-$(POETRY_VERSION)-py3-none-any.whl

# Service-specific Lambda names
DMS_DB_LAMBDA_NAME := ftrs-dos-$(ENVIRONMENT)-data-migration-dms-db-setup
FULL_REPLICATION_TASK_NAME := ftrs-dos-$(ENVIRONMENT)-data-migration-etl-full-replication-task
CDC_REPLICATION_TASK_NAME := ftrs-dos-$(ENVIRONMENT)-data-migration-etl-cdc-replication-task
WAIT_SECONDS ?= 30

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Targets
# ==============================================================================

export-to-s3: install
	poetry run dos-etl export-to-s3 --env $(ENVIRONMENT)

restore-from-s3: install
	poetry run dos-etl restore-from-s3 --env $(ENVIRONMENT) --workspace $(WORKSPACE)

invoke-replication-task:
	@echo "Checking status of replication task $(FULL_REPLICATION_TASK_NAME)..."
	$(eval TASK_STATUS := $(shell aws dms describe-replication-tasks --query "ReplicationTasks[?ReplicationTaskIdentifier=='$(FULL_REPLICATION_TASK_NAME)'].Status | [0]" --output text))
	@echo "Current task status: $(TASK_STATUS)"
	@if [ "$(TASK_STATUS)" = "ready" ]; then \
		echo "Starting replication task with start-replication..."; \
		aws dms start-replication-task \
		--replication-task-arn $(shell aws dms describe-replication-tasks --query "ReplicationTasks[?ReplicationTaskIdentifier=='$(FULL_REPLICATION_TASK_NAME)'].ReplicationTaskArn | [0]" --output text) \
		--start-replication-task-type start-replication; \
	else \
		echo "Task is currently in status $(TASK_STATUS), which is not 'ready'. Skipping start-replication."; \
	fi

	@echo "Checking status of CDC replication task $(CDC_REPLICATION_TASK_NAME)..."
	$(eval CDC_TASK_STATUS := $(shell aws dms describe-replication-tasks --query "ReplicationTasks[?ReplicationTaskIdentifier=='$(CDC_REPLICATION_TASK_NAME)'].Status | [0]" --output text))
	@echo "Current CDC task status: $(CDC_TASK_STATUS)"
	@if [ "$(CDC_TASK_STATUS)" = "ready" ]; then \
		echo "Starting CDC replication task with start-replication..."; \
		aws dms start-replication-task \
		--replication-task-arn $(shell aws dms describe-replication-tasks --query "ReplicationTasks[?ReplicationTaskIdentifier=='$(CDC_REPLICATION_TASK_NAME)'].ReplicationTaskArn | [0]" --output text) \
		--start-replication-task-type start-replication; \
	else \
		echo "CDC task is currently in status $(CDC_TASK_STATUS), which is not 'ready'. Skipping start-replication."; \
	fi

	@echo "Continuing with remaining steps..."
	@echo "Waiting for $(WAIT_SECONDS) seconds after replication task check..."
	@sleep $(WAIT_SECONDS)

invoke-lambda:
	aws lambda invoke \
	--function-name $(DMS_DB_LAMBDA_NAME) \
	/dev/null

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "Data Migration Service Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install                  - Install dependencies"
	@echo "  make lint                     - Run linting checks"
	@echo "  make test                     - Run tests"
	@echo "  make build                    - Build Lambda package"
	@echo ""
	@echo "Data Operations:"
	@echo "  make export-to-s3             - Export data to S3"
	@echo "  make restore-from-s3          - Restore data from S3"
	@echo "  make invoke-replication-task  - Start DMS replication task"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish                  - Publish to development"
	@echo "  make stage-release            - Stage release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                    - Clean build artifacts"
