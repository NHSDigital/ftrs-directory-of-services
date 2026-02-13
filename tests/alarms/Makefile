# ==============================================================================
# Warning Lambda Alarms
# ==============================================================================

# These are currently placeholders and will be revised to trigger actual alarms once the baseline metrics are established.

test-lambda-alarm-errors-warning: # Trigger error WARNING alarm for search Lambda
	./scripts/trigger-alarms.sh errors search 2

test-lambda-alarm-duration-p95: # Trigger duration p95 WARNING alarm for search Lambda
	./scripts/trigger-alarms.sh duration-p95 search 5

test-lambda-alarm-concurrent-warning: # Trigger concurrent executions WARNING alarm for search Lambda (>= 80)
	./scripts/trigger-alarms.sh concurrent search 85

# ==============================================================================
# Critical Lambda Alarms
# ==============================================================================

test-lambda-alarm-errors-critical: # Trigger error CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh errors search 2

test-lambda-alarm-errors-health-critical: # Trigger error CRITICAL alarm for health check Lambda
	./scripts/trigger-alarms.sh errors health-check 2

test-lambda-alarm-duration-p99-critical: # Trigger duration p99 CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh duration-p99 search 5

test-lambda-alarm-concurrent-critical: # Trigger concurrent executions CRITICAL alarm for search Lambda (>= 100)
	./scripts/trigger-alarms.sh concurrent search 105

test-lambda-alarm-throttles-critical: # Trigger throttle CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh throttles search 20

test-lambda-alarm-invocations-spike: # Trigger invocations spike CRITICAL alarm for search Lambda
	./scripts/trigger-alarms.sh invocations-spike search 650
