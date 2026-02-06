@crud-org-api @ftrs-pipeline @aws-smoke
Feature: Organization API Endpoint - AWS Smoke Tests

  # ============================================================================
  # AWS SMOKE TESTS ONLY
  # ============================================================================
  # These tests verify AWS-specific infrastructure that LocalStack cannot test:
  #   - mTLS certificate authentication
  #   - APIM gateway connectivity
  #   - DNS resolution
  #   - Deployed endpoint availability
  #
  # Comprehensive business logic tests (validation, sanitization, etc.) are in:
  #   tests/step_definitions/local_steps/test_crud_apis_organization_comprehensive.py
  #
  # Run LocalStack tests with: make test-local-crud-apis-comprehensive
  # ============================================================================

  # ---------------------------------------------------------------------------
  # Connectivity & Health Checks
  # ---------------------------------------------------------------------------

  Scenario: Smoke test - Organization endpoint is reachable
    When I request data from the "crud" endpoint "Organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle

  Scenario: Smoke test - Organization GET by ID works
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json" with specific id
    When I request data from the "crud" endpoint "Organization" with the seeded ID
    Then I receive a status code "200" in response

  # ---------------------------------------------------------------------------
  # mTLS Authentication (AWS-specific)
  # ---------------------------------------------------------------------------

  Scenario: Smoke test - Update organization with valid mTLS credentials
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json" with specific id
    When I update the organization details for ODS Code
    Then I receive a status code "200" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains an issue with severity "information"

  # ---------------------------------------------------------------------------
  # Basic Validation (single representative test per category)
  # ---------------------------------------------------------------------------

  Scenario: Smoke test - Invalid Content-Type is rejected
    When I send a PUT request with invalid Content-Type to the organization API
    Then I receive a status code "415" in response
    And the response body contains an "OperationOutcome" resource

  Scenario: Smoke test - Missing required field is rejected
    When I remove the "name" field from the payload and update the organization
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource

  Scenario: Smoke test - Non-existent organization returns 404
    When I update the organization with a non-existent ID
    Then I receive a status code "404" in response
    And the response body contains an "OperationOutcome" resource

  # ---------------------------------------------------------------------------
  # Database Connectivity (verify DynamoDB is accessible)
  # ---------------------------------------------------------------------------

  Scenario: Smoke test - Data persists to database after update
    Given that the stack is "organisation"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json" with specific id
    When I update the organization details for ODS Code
    Then I receive a status code "200" in response
    And the data in the database matches the inserted payload
