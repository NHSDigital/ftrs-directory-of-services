@local-etl-ods
Feature: ETL ODS Local - Pipeline Testing with Testcontainers

  This feature tests the ETL ODS pipeline locally using:
  - LocalStack for AWS services (SQS, DynamoDB, Secrets Manager)
  - Mock ODS Terminology API server
  - Local CRUD APIs server
  - Direct Lambda handler invocation

  These tests can run without AWS deployment when USE_LOCALSTACK=true.

  Background:
    Given the ETL ODS local test environment is configured
    And I have the ODS mock server running

  @local-etl-ods-extractor
  Scenario: Extractor successfully processes organizations - Happy Path
    When I run the ETL ODS extractor for date "2025-12-08"
    Then the extractor should return status code 200
    And the extractor should successfully process organizations

  @local-etl-ods-extractor
  Scenario: Extractor handles empty results gracefully
    When I run the ETL ODS extractor for date "2025-12-09"
    Then the extractor should return status code 200
    And the extractor should return an empty result

  @local-etl-ods-extractor
  Scenario: Extractor uses happy path scenario fixture
    When I run the ETL ODS extractor for happy path scenario
    Then the extractor should successfully process organizations

  @local-etl-ods-extractor
  Scenario: Extractor uses empty payload scenario fixture
    When I run the ETL ODS extractor for empty payload scenario
    Then the extractor should return an empty result

  @local-etl-ods-full-pipeline @slow @wip
  Scenario: Full pipeline processes organizations end-to-end
    # NOTE: This test requires additional JWT auth configuration for the transformer.
    # The transformer needs LOCAL_PRIVATE_KEY, LOCAL_KID, and LOCAL_TOKEN_URL env vars.
    When I run the full ETL ODS pipeline for date "2025-12-08"
    Then the pipeline should complete without errors
    And the pipeline should process 2 organizations
