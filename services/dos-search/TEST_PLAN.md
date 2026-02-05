# DoS Search Service - Test Plan

**Service**: Directory of Services (DoS) Search - ODS Organization Lookup
**Version**: 1.0
**Date**: 2026-02-04
**Status**: Ready for Review

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Coverage Overview](#test-coverage-overview)
3. [Unit Tests](#unit-tests)
4. [Smoke Tests](#smoke-tests)
5. [Test Execution Strategy](#test-execution-strategy)
6. [Environment Configuration](#environment-configuration)
7. [Success Criteria](#success-criteria)
8. [Appendix](#appendix)

---

## Executive Summary

This test plan defines the comprehensive testing strategy for the DoS Search service following APIM and Logging development completion. The plan covers:

- **Unit Tests**: 82+ existing tests + 45+ new tests = **127+ total unit tests**
- **Smoke Tests**: 35+ new tests for higher environments
- **Coverage**: FHIR R4B schema validation, API Gateway errors, header handling, ODS lookup scenarios

### Key Additions

| Category | Tests Added | Purpose |
|----------|-------------|---------|
| FHIR Schema Validation | 22 tests | Validate compliance with FHIR R4B specification |
| API Gateway Errors | 18 tests | Validate API Gateway-specific error scenarios |
| Minimal Headers | 2 tests | Validate requests with minimal/no headers |
| Smoke Tests | 35+ tests | Validate deployed service functionality |

---

## Test Coverage Overview

### Coverage Matrix

| Test Category | Unit | Smoke | Priority | Frequency |
|--------------|------|-------|----------|-----------|
| **Response Schema** | ✅ 22 tests | ✅ 12 tests | 🔴 CRITICAL | Unit: Every commit<br>Smoke: Hourly |
| **Empty Bundle** | ✅ 1 test | ✅ 2 tests | 🔴 CRITICAL | Unit: Every commit<br>Smoke: Hourly |
| **Full Schema** | ✅ 22 tests | ✅ 12 tests | 🔴 CRITICAL | Unit: Every commit<br>Smoke: Hourly |
| **No Matching ODS** | ✅ 1 test | ✅ 3 tests | 🟡 MEDIUM | Unit: Every commit<br>Smoke: Hourly |
| **With Headers** | ✅ 21 tests | ✅ 2 tests | 🟡 MEDIUM | Unit: Every commit<br>Smoke: Daily |
| **Without Headers** | ✅ 2 tests | ✅ 1 test | 🟢 LOW | Unit: Every commit<br>Smoke: Daily |
| **Lambda Errors** | ✅ 3 tests | - | 🟡 MEDIUM | Unit: Every commit |
| **API Gateway Errors** | ✅ 18 tests | - | 🟡 MEDIUM | Unit: Every commit |

### Test Files Summary

#### Unit Tests (9 files, 127+ tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_fhir_schema_validation.py` | 22 | **NEW** - FHIR R4B compliance |
| `test_api_gateway_errors.py` | 18 | **NEW** - API Gateway scenarios |
| `test_dos_search_ods_code_function.py` | 9 | **UPDATED** - Added minimal headers |
| `test_bundle_mapper.py` | 9 | FHIR Bundle mapping |
| `test_endpoint_mapper.py` | 20+ | FHIR Endpoint mapping |
| `test_organization_mapper.py` | 4 | FHIR Organization mapping |
| `test_error_util.py` | 15+ | Error handling utilities |
| `test_organization_query_params.py` | 9 | Query parameter validation |
| `test_ftrs_service.py` | 5 | Service layer orchestration |

#### Smoke Tests (3 files, 35+ tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_smoke_health_check.py` | 8 | **NEW** - Health endpoint |
| `test_smoke_ods_lookup.py` | 15+ | **NEW** - ODS search scenarios |
| `test_smoke_schema_validation.py` | 12+ | **NEW** - FHIR compliance in production |

---

## Unit Tests

### 1. FHIR R4B Schema Validation Tests

**File**: `services/dos-search/tests/unit/functions/ftrs_service/fhir_mapper/test_fhir_schema_validation.py`

**Purpose**: Validate that all generated FHIR resources comply with the official FHIR R4B specification.

**Test Classes**:

#### TestBundleSchemaValidation (6 tests)

- ✅ `test_bundle_validates_against_fhir_r4b_schema` - Full bundle validation
- ✅ `test_empty_bundle_validates_against_fhir_r4b_schema` - Empty bundle validation
- ✅ `test_bundle_with_multiple_endpoints_validates_schema` - Multiple endpoints
- ✅ `test_bundle_link_structure_complies_with_schema` - Link structure
- ✅ `test_bundle_entry_search_mode_complies_with_schema` - Search mode values
- ✅ `test_organization_entry_has_match_mode` - Organization search mode

#### TestOrganizationSchemaValidation (5 tests)

- ✅ `test_organization_validates_against_fhir_r4b_schema` - Organization validation
- ✅ `test_organization_identifier_system_complies_with_schema` - Identifier system
- ✅ `test_organization_with_different_active_states` - Active field validation
- ✅ `test_organization_name_field_complies_with_schema` - Name field validation
- ✅ Tests various name formats (spaces, hyphens, apostrophes, long names)

#### TestEndpointSchemaValidation (6 tests)

- ✅ `test_endpoint_validates_against_fhir_r4b_schema` - Endpoint validation
- ✅ `test_endpoint_status_field_uses_valid_fhir_values` - Status validation
- ✅ `test_endpoint_connection_type_coding_complies_with_schema` - Connection type
- ✅ `test_endpoint_payload_type_structure_complies_with_schema` - Payload type
- ✅ `test_endpoint_payload_mime_type_is_valid` - MIME type validation
- ✅ `test_endpoint_address_field_accepts_various_formats` - Address formats

#### TestEndpointExtensionsSchemaValidation (4 tests)

- ✅ `test_order_extension_complies_with_schema` - Order extension
- ✅ `test_compression_extension_complies_with_schema` - Compression extension
- ✅ `test_business_scenario_extension_complies_with_schema` - Business scenario
- ✅ `test_multiple_extensions_on_single_endpoint` - Multiple extensions

#### TestFullBundleSchemaCompliance (3 tests)

- ✅ `test_complete_bundle_with_all_elements_validates` - Full integration
- ✅ `test_bundle_serialization_produces_valid_json` - JSON serialization
- ✅ `test_invalid_data_raises_validation_error` - Negative test

**Dependencies**: `fhir.resources>=8.0.0` (already in project dependencies)

---

### 2. API Gateway Error Scenario Tests

**File**: `services/dos-search/tests/unit/functions/test_api_gateway_errors.py`

**Purpose**: Validate handling of API Gateway-specific error scenarios.

**Test Classes**:

#### TestAPIGatewayMalformedRequests (5 tests)

- ✅ `test_missing_http_method` - Missing httpMethod field
- ✅ `test_missing_query_string_parameters` - None queryStringParameters
- ✅ `test_empty_query_string_parameters` - Empty dict
- ✅ `test_missing_headers` - None headers
- ✅ `test_empty_headers` - Empty headers dict

#### TestAPIGatewayUnsupportedMethods (2 tests)

- ✅ `test_unsupported_http_methods` - POST, PUT, DELETE, PATCH, OPTIONS, HEAD
- ✅ `test_case_sensitive_http_method` - Lowercase method

#### TestAPIGatewayRequestEdgeCases (4 tests)

- ✅ `test_extra_unexpected_fields_in_event` - Extra event fields
- ✅ `test_case_insensitive_header_names` - Header name casing
- ✅ `test_multivalue_query_parameters` - MultiValue parameters
- ✅ `test_duplicate_query_parameters` - Duplicate params

#### TestAPIGatewayResponseFormat (4 tests)

- ✅ `test_response_has_required_fields` - statusCode and body
- ✅ `test_response_body_is_valid_json` - JSON validation
- ✅ `test_response_includes_cors_headers` - CORS headers
- ✅ `test_response_content_type_is_fhir_json` - Content-Type header

#### TestAPIGatewayPayloadSizeHandling (3 tests)

- ✅ `test_large_ods_code_value` - Maximum length ODS code
- ✅ `test_oversized_ods_code_rejected` - Exceeds maximum
- ✅ `test_large_number_of_headers` - Many headers

#### TestAPIGatewayContextHandling (2 tests)

- ✅ `test_lambda_context_with_request_id` - Context attributes
- ✅ `test_lambda_context_none` - None context handling

**Total**: 18 tests

---

### 3. Minimal Headers Tests

**File**: `services/dos-search/tests/unit/functions/test_dos_search_ods_code_function.py` (updated)

**Purpose**: Validate requests with minimal or no headers.

**New Tests**:

- ✅ `test_lambda_handler_with_minimal_headers` - Empty headers dict
- ✅ `test_lambda_handler_without_headers_field` - Missing headers field

---

### 4. Existing Unit Tests (Retained)

All existing unit tests remain in place:

- **test_bundle_mapper.py** (9 tests) - Bundle creation, empty bundles
- **test_endpoint_mapper.py** (20+ tests) - Endpoint mapping, extensions
- **test_organization_mapper.py** (4 tests) - Organization mapping
- **test_dos_search_ods_code_function.py** (7 tests + 2 new) - Lambda handler
- **test_error_util.py** (15+ tests) - Error outcomes
- **test_organization_query_params.py** (9 tests) - Query validation
- **test_ftrs_service.py** (5 tests) - Service layer
- **test_health_check_function.py** (3 tests) - Health check
- **test_temporary_sgsd_setup.py** (10 tests) - Index population

---

## Smoke Tests

Smoke tests validate critical functionality in deployed environments (dev, test, int, prod).

### Configuration

Smoke tests use environment variables for configuration:

```text
# Required
SMOKE_TEST_BASE_URL=https://api.example.com/dos-search

# Optional
SMOKE_TEST_API_KEY=your-api-key
SMOKE_TEST_VALID_ODS_CODE=ABC123
SMOKE_TEST_INVALID_ODS_CODE=INVALID!
SMOKE_TEST_NONEXISTENT_ODS_CODE=NOEXIST99
SMOKE_TEST_TIMEOUT=10
SMOKE_TEST_ENVIRONMENT=test  # local, dev, test, int, prod
```

### Execution

```bash
# Run all smoke tests
pytest tests/smoke -m smoke

# Run specific smoke test file
pytest tests/smoke/test_smoke_health_check.py

# Run smoke tests for specific environment
SMOKE_TEST_ENVIRONMENT=test pytest tests/smoke -m smoke

# Exclude smoke tests from unit test runs
pytest tests/unit -m "not smoke"
```

---

### 1. Health Check Smoke Tests

**File**: `services/dos-search/tests/smoke/test_smoke_health_check.py`

**Frequency**: Every 5 minutes in production

**Test Classes**:

#### TestHealthCheckSmoke (6 tests)

- ✅ `test_health_endpoint_returns_200` - **CRITICAL** - Service availability
- ✅ `test_health_endpoint_response_time` - Response < 2 seconds
- ✅ `test_health_endpoint_returns_json` - Valid JSON response
- ✅ `test_health_endpoint_contains_status` - Status information
- ✅ `test_health_endpoint_no_authentication_required` - No auth needed

#### TestHealthCheckResilience (2 tests)

- ✅ `test_health_check_handles_concurrent_requests` - Concurrent load
- ✅ `test_health_check_with_invalid_method` - Method validation

**Total**: 8 tests

---

### 2. ODS Lookup Smoke Tests

**File**: `services/dos-search/tests/smoke/test_smoke_ods_lookup.py`

**Frequency**: Every 15 minutes in production

**Test Classes**:

#### TestODSLookupSmoke (5 tests)

- ✅ `test_valid_ods_lookup_returns_200` - **CRITICAL** - Core functionality
- ✅ `test_valid_ods_lookup_returns_fhir_bundle` - FHIR Bundle response
- ✅ `test_valid_ods_lookup_bundle_has_entries` - Data presence
- ✅ `test_valid_ods_lookup_response_time` - Response < 5 seconds

#### TestInvalidODSCodeSmoke (4 tests)

- ✅ `test_invalid_ods_format_returns_400` - **CRITICAL** - Error handling
- ✅ `test_invalid_ods_returns_operation_outcome` - FHIR OperationOutcome
- ✅ `test_too_short_ods_code_rejected` - Minimum length validation
- ✅ `test_too_long_ods_code_rejected` - Maximum length validation

#### TestNonexistentODSCodeSmoke (2 tests)

- ✅ `test_nonexistent_ods_returns_empty_bundle` - **CRITICAL** - Empty results
- ✅ `test_nonexistent_ods_bundle_has_self_link` - Bundle structure

#### TestQueryParameterValidationSmoke (5 tests)

- ✅ `test_missing_identifier_parameter` - Required parameter
- ✅ `test_missing_revinclude_parameter` - Required parameter
- ✅ `test_wrong_identifier_system` - System validation
- ✅ `test_wrong_revinclude_value` - Value validation
- ✅ `test_extra_query_parameters_rejected` - Strict validation

#### TestHeaderValidationSmoke (2 tests)

- ✅ `test_invalid_custom_header_rejected` - Invalid header rejection
- ✅ `test_valid_nhsd_headers_accepted` - Valid NHSD headers

**Total**: 18 tests

---

### 3. Schema Validation Smoke Tests

**File**: `services/dos-search/tests/smoke/test_smoke_schema_validation.py`

**Frequency**: Hourly in production

**Test Classes**:

#### TestFHIRSchemaComplianceSmoke (5 tests)

- ✅ `test_bundle_response_validates_against_fhir_schema` - **CRITICAL** - Bundle validation
- ✅ `test_organization_resource_validates_against_schema` - Organization validation
- ✅ `test_endpoint_resources_validate_against_schema` - Endpoint validation
- ✅ `test_empty_bundle_validates_against_schema` - Empty bundle validation
- ✅ `test_operation_outcome_validates_against_schema` - Error validation

#### TestBundleStructureCompliance (5 tests)

- ✅ `test_bundle_has_required_type_field` - Type field presence
- ✅ `test_bundle_has_self_link` - Self link presence
- ✅ `test_bundle_entries_have_search_mode` - Search mode field
- ✅ `test_organization_entry_has_match_mode` - Match mode
- ✅ `test_endpoint_entries_have_include_mode` - Include mode

#### TestOrganizationResourceCompliance (2 tests)

- ✅ `test_organization_has_identifier` - Identifier presence
- ✅ `test_organization_has_active_field` - Active field

#### TestEndpointResourceCompliance (2 tests)

- ✅ `test_endpoint_has_required_fields` - Required fields
- ✅ `test_endpoint_connection_type_uses_valid_coding` - Coding system

**Total**: 14 tests

---

## Test Execution Strategy

### Development Environment

**Run all unit tests**:

```bash
cd services/dos-search
pytest tests/unit -v --cov=functions --cov=health_check --cov-report=term-missing
```

**Run specific test file**:

```bash
pytest tests/unit/functions/ftrs_service/fhir_mapper/test_fhir_schema_validation.py -v
```

**Run tests with coverage threshold**:

```bash
pytest tests/unit --cov-fail-under=80
```

---

### CI/CD Pipeline

**Pre-commit**:

- Linting (ruff)
- Unit tests (all 127+ tests)
- Coverage threshold: 80%

**Build Stage**:

```bash
# Install dependencies
poetry install --with test

# Run unit tests with coverage
poetry run pytest tests/unit -v \
  --cov=functions \
  --cov=health_check \
  --cov-fail-under=80 \
  --cov-branch

# Generate coverage report
poetry run pytest tests/unit --cov-report=html
```

**Deployment to Dev**:

- Unit tests pass ✅
- Coverage ≥ 80% ✅
- Build successful ✅

---

### Smoke Test Execution

#### Development Environment

```bash
# Run smoke tests against local endpoint
SMOKE_TEST_BASE_URL=http://localhost:3000 \
SMOKE_TEST_VALID_ODS_CODE=ABC123 \
pytest tests/smoke -m smoke -v
```

#### Test Environment

**Schedule**:

- Health checks: Every 5 minutes
- ODS lookup: Every 15 minutes
- Schema validation: Every hour

**Execution**:

```bash
# Run all smoke tests
SMOKE_TEST_BASE_URL=https://test.api.example.com \
SMOKE_TEST_ENVIRONMENT=test \
SMOKE_TEST_VALID_ODS_CODE=TEST123 \
SMOKE_TEST_API_KEY=$TEST_API_KEY \
pytest tests/smoke -m smoke -v

# Run critical smoke tests only
pytest tests/smoke -m smoke -k "CRITICAL" -v
```

#### Production Environment

**Schedule**:

- Health checks: Every 5 minutes
- ODS lookup (critical): Every 15 minutes
- ODS lookup (full): Every hour
- Schema validation: Every hour

**Execution**:

```bash
SMOKE_TEST_BASE_URL=https://api.nhs.uk/dos-search \
SMOKE_TEST_ENVIRONMENT=prod \
SMOKE_TEST_VALID_ODS_CODE=PROD123 \
SMOKE_TEST_API_KEY=$PROD_API_KEY \
pytest tests/smoke -m smoke --tb=short
```

**Alerting**:

- Smoke test failures trigger PagerDuty alerts
- Critical tests (marked **CRITICAL**) have P1 priority
- Non-critical tests have P2 priority

---

## Environment Configuration

### Test Environments

| Environment | Base URL | Purpose | Smoke Tests |
|-------------|----------|---------|-------------|
| **Local** | <http://localhost:3000> | Development | Manual only |
| **Dev** | <https://dev.api.example.com> | Integration testing | On-demand |
| **Test** | <https://test.api.example.com> | Pre-production validation | Every 15 min |
| **Int** | <https://int.api.example.com> | Integration validation | Every 15 min |
| **Prod** | <https://api.nhs.uk/dos-search> | Live service | Every 5-15 min |

### Required Environment Variables (Smoke Tests)

```bash
# Test
export SMOKE_TEST_BASE_URL=https://test.api.example.com
export SMOKE_TEST_ENVIRONMENT=test
export SMOKE_TEST_VALID_ODS_CODE=ABC123
export SMOKE_TEST_NONEXISTENT_ODS_CODE=NOEXIST99
export SMOKE_TEST_INVALID_ODS_CODE=INVALID!
export SMOKE_TEST_API_KEY=$TEST_API_KEY
export SMOKE_TEST_TIMEOUT=10

# Production
export SMOKE_TEST_BASE_URL=https://api.nhs.uk/dos-search
export SMOKE_TEST_ENVIRONMENT=prod
export SMOKE_TEST_VALID_ODS_CODE=RX809  # Known valid ODS code
export SMOKE_TEST_NONEXISTENT_ODS_CODE=ZZZZ999
export SMOKE_TEST_INVALID_ODS_CODE=INVALID!
export SMOKE_TEST_API_KEY=$PROD_API_KEY
export SMOKE_TEST_TIMEOUT=10
```

---

## Success Criteria

### Unit Tests

- ✅ All 127+ unit tests pass
- ✅ Code coverage ≥ 80%
- ✅ Branch coverage ≥ 80%
- ✅ No new linting errors (ruff)
- ✅ All FHIR R4B schema validation tests pass
- ✅ All API Gateway error scenarios handled

### Smoke Tests

#### Test/Int Environments

- ✅ 100% smoke test pass rate for 24 hours
- ✅ Health check response time < 2 seconds
- ✅ ODS lookup response time < 5 seconds
- ✅ All FHIR responses validate against R4B schema

#### Production

- ✅ 99.9% smoke test pass rate
- ✅ Health check response time < 2 seconds (95th percentile)
- ✅ ODS lookup response time < 5 seconds (95th percentile)
- ✅ Zero schema validation failures
- ✅ Zero critical smoke test failures for 7 days

---

## Appendix

### A. Test Markers

Pytest markers for organizing test execution:

```python
# Smoke tests (run in deployed environments)
@pytest.mark.smoke

# Unit tests (default)
@pytest.mark.unit
```

**Usage**:

```bash
# Run only smoke tests
pytest -m smoke

# Run only unit tests
pytest -m unit

# Exclude smoke tests
pytest -m "not smoke"
```

---

### B. Test Dependencies

**Production Dependencies** (already in project):

```toml
fhir-resources = ">=8.0.0,<9.0.0"
pydantic = ">=2.11.4,<3.0.0"
```

**Test Dependencies** (updated):

```toml
[tool.poetry.group.test.dependencies]
pytest = "^8.3.5"
pytest-mock = "^3.14.0"
pytest-cov = "^6.1.1"
requests = "^2.32.0"  # NEW - for smoke tests
```

---

### C. Coverage Reports

**Generate HTML coverage report**:

```bash
pytest tests/unit --cov=functions --cov=health_check --cov-report=html
open htmlcov/index.html
```

**Generate XML coverage report** (for CI/CD):

```bash
pytest tests/unit --cov=functions --cov=health_check --cov-report=xml
```

---

### D. Continuous Integration Example

**GitHub Actions Workflow**:

```yaml
name: Test dos-search

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd services/dos-search
          pip install poetry
          poetry install --with test

      - name: Run unit tests
        run: |
          cd services/dos-search
          poetry run pytest tests/unit -v \
            --cov=functions \
            --cov=health_check \
            --cov-fail-under=80 \
            --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./services/dos-search/coverage.xml

  smoke-tests-test:
    runs-on: ubuntu-latest
    needs: unit-tests
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd services/dos-search
          pip install poetry
          poetry install --with test

      - name: Run smoke tests
        env:
          SMOKE_TEST_BASE_URL: ${{ secrets.TEST_BASE_URL }}
          SMOKE_TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
          SMOKE_TEST_ENVIRONMENT: test
        run: |
          cd services/dos-search
          poetry run pytest tests/smoke -m smoke -v
```

---

### E. Test File Locations

**Unit Tests**:

```text
services/dos-search/tests/unit/
├── conftest.py
├── functions/
│   ├── test_dos_search_ods_code_function.py (UPDATED)
│   ├── test_error_util.py
│   ├── test_organization_query_params.py
│   ├── test_api_gateway_errors.py (NEW)
│   └── ftrs_service/
│       ├── test_ftrs_service.py
│       └── fhir_mapper/
│           ├── test_bundle_mapper.py
│           ├── test_endpoint_mapper.py
│           ├── test_organization_mapper.py
│           └── test_fhir_schema_validation.py (NEW)
├── health_check/
│   └── test_health_check_function.py
└── opensearch_local_index_populator/
    └── test_temporary_sgsd_setup.py
```

**Smoke Tests**:

```text
services/dos-search/tests/smoke/
├── __init__.py (NEW)
├── conftest.py (NEW)
├── test_smoke_health_check.py (NEW)
├── test_smoke_ods_lookup.py (NEW)
└── test_smoke_schema_validation.py (NEW)
```

---

### F. Known Test Data

For smoke tests in each environment:

**Test**:

- Valid ODS Code: `ABC123` (configure per environment)
- Nonexistent ODS Code: `NOEXIST99`
- Invalid ODS Code: `INVALID!`

**Production**:

- Valid ODS Code: `RX809` (Royal Devon University Healthcare NHS Foundation Trust)
- Nonexistent ODS Code: `ZZZZ999`
- Invalid ODS Code: `INVALID!`

---

### G. Troubleshooting

**Unit tests failing with "fhir.resources not found"**:

```bash
# Reinstall dependencies
poetry install --with test
```

**Smoke tests timing out**:

```bash
# Increase timeout
export SMOKE_TEST_TIMEOUT=30
pytest tests/smoke -m smoke
```

**Coverage below 80%**:

```bash
# Generate detailed coverage report
pytest tests/unit --cov=functions --cov-report=term-missing
# Check which lines are missing coverage
```

**Schema validation failures**:

```bash
# Run specific schema test with verbose output
pytest tests/unit/functions/ftrs_service/fhir_mapper/test_fhir_schema_validation.py -v -s
```

---

## Summary

This test plan provides comprehensive coverage for the DoS Search service:

- **127+ unit tests** covering FHIR mapping, validation, error handling, and API Gateway scenarios
- **35+ smoke tests** for validating deployed service functionality
- **FHIR R4B schema compliance** validated in both unit and smoke tests
- **Clear execution strategy** for development, CI/CD, and production environments
- **Defined success criteria** for each environment

All missing tests identified in the original requirements have been implemented and documented.

---

**Next Steps**:

1. ✅ Run unit tests locally: `pytest tests/unit -v`
2. ✅ Verify coverage: `pytest tests/unit --cov=functions --cov=health_check`
3. ✅ Install smoke test dependencies: `poetry install --with test`
4. ✅ Configure environment variables for smoke tests
5. ✅ Run smoke tests against test environment: `pytest tests/smoke -m smoke`
6. ✅ Review and approve test plan
7. ✅ Integrate into CI/CD pipeline
8. ✅ Schedule production smoke tests

---

**Document Version**: 1.0
**Last Updated**: 2026-02-04
**Prepared By**: DoS Development Team
