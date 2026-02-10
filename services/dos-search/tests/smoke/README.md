# DoS Search - Smoke Tests

Smoke tests for validating deployed dos-search service functionality in higher environments.

## Overview

These tests validate critical functionality against deployed endpoints and should be run:

- **Health checks**: Every 5 minutes
- **ODS lookup (critical)**: Every 15 minutes
- **Schema validation**: Every hour

## Quick Start

### 1. Install Dependencies

```bash
cd services/dos-search
poetry install --with test
```

### 2. Configure Environment

```bash
# Required
export SMOKE_TEST_BASE_URL=https://staging.api.example.com

# Optional (with defaults)
export SMOKE_TEST_API_KEY=your-api-key              # Default: None
export SMOKE_TEST_VALID_ODS_CODE=ABC123             # Default: ABC123
export SMOKE_TEST_INVALID_ODS_CODE=INVALID!         # Default: INVALID!
export SMOKE_TEST_NONEXISTENT_ODS_CODE=NOEXIST99    # Default: NOEXIST99
export SMOKE_TEST_TIMEOUT=10                        # Default: 10
export SMOKE_TEST_ENVIRONMENT=staging               # Default: local
```

### 3. Run Tests

```bash
# Run all smoke tests
pytest tests/smoke -m smoke -v

# Run specific test file
pytest tests/smoke/test_smoke_health_check.py -v

# Run only critical tests
pytest tests/smoke -m smoke -k "CRITICAL" -v

# Run with detailed output
pytest tests/smoke -m smoke -v -s
```

## Test Files

### test_smoke_health_check.py (8 tests)

Validates health check endpoint availability and performance.

**Frequency**: Every 5 minutes

**Tests**:

- Health endpoint returns 200
- Response time < 2 seconds
- Returns valid JSON
- No authentication required
- Handles concurrent requests
- Rejects invalid methods

### test_smoke_ods_lookup.py (18 tests)

Validates core ODS organization lookup functionality.

**Frequency**: Every 15 minutes

**Tests**:

- Valid ODS lookup returns 200
- Returns FHIR bundle with entries
- Invalid ODS format returns 400
- Empty bundle for nonexistent ODS
- Query parameter validation
- Header validation

### test_smoke_schema_validation.py (14 tests)

Validates FHIR R4B schema compliance in production.

**Frequency**: Every hour

**Tests**:

- Bundle validates against FHIR R4B schema
- Organization resource compliance
- Endpoint resource compliance
- Empty bundle validation
- OperationOutcome validation

## Environment Configuration

### Local Development

```bash
export SMOKE_TEST_BASE_URL=http://localhost:3000
export SMOKE_TEST_ENVIRONMENT=local
pytest tests/smoke -m smoke
```

### Dev Environment

```bash
export SMOKE_TEST_BASE_URL=https://dev.api.example.com
export SMOKE_TEST_ENVIRONMENT=dev
export SMOKE_TEST_API_KEY=$DEV_API_KEY
export SMOKE_TEST_VALID_ODS_CODE=DEV123
pytest tests/smoke -m smoke
```

### Test Environment

```bash
export SMOKE_TEST_BASE_URL=https://test.api.example.com
export SMOKE_TEST_ENVIRONMENT=test
export SMOKE_TEST_API_KEY=$TEST_API_KEY
export SMOKE_TEST_VALID_ODS_CODE=TEST123
pytest tests/smoke -m smoke
```

### Int Environment

```bash
export SMOKE_TEST_BASE_URL=https://int.api.example.com
export SMOKE_TEST_ENVIRONMENT=int
export SMOKE_TEST_API_KEY=$INT_API_KEY
export SMOKE_TEST_VALID_ODS_CODE=INT123
pytest tests/smoke -m smoke
```

### Production

```bash
export SMOKE_TEST_BASE_URL=https://api.nhs.uk/dos-search
export SMOKE_TEST_ENVIRONMENT=production
export SMOKE_TEST_API_KEY=$PROD_API_KEY
export SMOKE_TEST_VALID_ODS_CODE=RX809  # Known valid ODS code
pytest tests/smoke -m smoke --tb=short
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Smoke Tests
  env:
    SMOKE_TEST_BASE_URL: ${{ secrets.TEST_BASE_URL }}
    SMOKE_TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
    SMOKE_TEST_ENVIRONMENT: test
  run: |
    cd services/dos-search
    poetry run pytest tests/smoke -m smoke -v
```

### Scheduled Execution

Use scheduled pipelines or task schedulers:

```bash
# Every 5 minutes - health checks
*/5 * * * * cd /path/to/dos-search && pytest tests/smoke/test_smoke_health_check.py -m smoke

# Every 15 minutes - critical ODS lookups
*/15 * * * * cd /path/to/dos-search && pytest tests/smoke -m smoke -k "CRITICAL"

# Hourly - full smoke test suite
0 * * * * cd /path/to/dos-search && pytest tests/smoke -m smoke
```

## Troubleshooting

### Connection Errors

```bash
# Check base URL is accessible
curl $SMOKE_TEST_BASE_URL/health

# Verify environment variables are set
env | grep SMOKE_TEST
```

### Timeout Issues

```bash
# Increase timeout
export SMOKE_TEST_TIMEOUT=30
pytest tests/smoke -m smoke
```

### Authentication Failures

```bash
# Verify API key is valid
curl -H "Authorization: Bearer $SMOKE_TEST_API_KEY" $SMOKE_TEST_BASE_URL/health

# Check if endpoint requires API key
pytest tests/smoke/test_smoke_health_check.py::TestHealthCheckSmoke::test_health_endpoint_no_authentication_required -v
```

### Test Data Issues

```bash
# Verify ODS codes exist in target environment
curl "$SMOKE_TEST_BASE_URL/Organization?identifier=odsOrganisationCode|$SMOKE_TEST_VALID_ODS_CODE&_revinclude=Endpoint:organization"
```

## Alerting

Configure alerts based on test results:

- **Critical test failures** → P1 PagerDuty alert
- **Non-critical failures** → P2 alert
- **Multiple consecutive failures** → Escalate to P1

Example alert conditions:

- Health check fails 3 times in 15 minutes → P1
- Schema validation fails → P2
- Response time > 5 seconds for 3 consecutive tests → P2

## Test Results

Smoke test results should be:

- **Logged** to monitoring system (CloudWatch, etc.)
- **Tracked** for trends and performance degradation
- **Reported** in dashboards for visibility

## Known Issues

None at this time.

## Support

For questions or issues with smoke tests:

1. Check [TEST_PLAN.md](../../TEST_PLAN.md) for detailed documentation
2. Review test output with `-v -s` flags for debugging
3. Contact the DoS development team

---

**Last Updated**: 2026-02-04
