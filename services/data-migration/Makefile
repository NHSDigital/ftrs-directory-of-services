# Data Migration Service Makefile
# This service handles data migration and ETL processes for the DoS platform

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= data-migration
POETRY_VERSION := $(shell poetry version -s)
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

export-to-s3: install ## Export data from the source database to S3
	poetry run dos-etl export-to-s3 --env $(ENVIRONMENT)

restore-from-s3: install ## Restore data from S3 to the source database
	poetry run dos-etl restore-from-s3 --env $(ENVIRONMENT) --workspace $(WORKSPACE)

invoke-replication-task: ## Invoke the DMS replication tasks (full load + CDC)
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

invoke-lambda: ## Invoke the DMS DB setup Lambda function
	aws lambda invoke \
	--function-name $(DMS_DB_LAMBDA_NAME) \
	/dev/null

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  Data Migration Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
