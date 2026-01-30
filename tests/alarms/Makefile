SERVICE ?= dos-search

# ==============================================================================
# Alarm Testing Targets
# ==============================================================================

test-lambda-alarm-errors-warning: # Trigger error WARNING alarm for search Lambda
	./scripts/trigger-alarms.sh errors search 2

test-lambda-alarm-errors-critical: # Trigger error CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh errors search 2

test-lambda-alarm-errors-health: # Trigger error CRITICAL alarm for health check Lambda
	./scripts/trigger-alarms.sh errors health-check 2

test-lambda-alarm-duration-p95: # Trigger duration p95 WARNING alarm for search Lambda
	./scripts/trigger-alarms.sh duration-p95 search 5

test-lambda-alarm-duration-p99: # Trigger duration p99 CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh duration-p99 search 5

test-lambda-alarm-concurrent-warning: # Trigger concurrent executions WARNING alarm for search Lambda (>= 80)
	./scripts/trigger-alarms.sh concurrent search 85

test-lambda-alarm-concurrent-critical: # Trigger concurrent executions CRITICAL alarm for search Lambda (>= 100)
	./scripts/trigger-alarms.sh concurrent search 105

test-lambda-alarm-throttles: # Trigger throttle CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh throttles search 20

test-lambda-alarm-invocations-spike: # Trigger invocations spike CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh invocations-spike search 650

test-lambda-alarms-all: # Trigger all testable alarms for search Lambda
	@echo "Testing all alarms for search Lambda..."
	@make test-lambda-alarm-errors-warning
	@sleep 5
	@make test-lambda-alarm-duration-p95
	@sleep 5
	@make test-lambda-alarm-concurrent-warning
