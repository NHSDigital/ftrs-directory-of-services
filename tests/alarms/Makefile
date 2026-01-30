SERVICE ?= dos-search

# ==============================================================================
# Alarm Testing Targets
# ==============================================================================

test-lambda-alarm-errors: # Trigger error alarm for search Lambda
	./scripts/trigger-alarms.sh errors search 10

test-lambda-alarm-errors-health: # Trigger error alarm for health check Lambda
	./scripts/trigger-alarms.sh errors health-check 10

test-lambda-alarm-duration: # Trigger duration alarm for search Lambda
	./scripts/trigger-alarms.sh duration search 5

test-lambda-alarm-duration-health: # Trigger duration alarm for health check Lambda
	./scripts/trigger-alarms.sh duration health-check 5

test-lambda-alarm-concurrent: # Trigger concurrent executions alarm for search Lambda
	./scripts/trigger-alarms.sh concurrent search 100

test-lambda-alarm-concurrent-health: # Trigger concurrent executions alarm for health check Lambda
	./scripts/trigger-alarms.sh concurrent health-check 10

test-lambda-alarm-throttles: # Trigger throttle alarm for search Lambda
	./scripts/trigger-alarms.sh throttles search 20

test-lambda-alarm-throttles-health: # Trigger throttle alarm for health check Lambda
	./scripts/trigger-alarms.sh throttles health-check 20

test-lambda-alarm-invocations: # Info on triggering low invocations alarm
	./scripts/trigger-alarms.sh invocations search

test-lambda-alarms-all: # Trigger all testable alarms for search Lambda
	@echo "Testing all alarms for search Lambda..."
	@make test-lambda-alarm-errors
	@sleep 5
	@make test-lambda-alarm-duration
	@sleep 5
	@make test-lambda-alarm-concurrent
