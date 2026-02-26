@is-smoke
Feature: dos-search smoke tests
# These tests are intended to be run in INT/REF/PROD environments against deployed dos-search instances, and should not rely on specific test data being present.
# They are designed to smoke test basic functionality of the dos-search API, and should not be testing edge cases or error conditions that require specific data to be present.
Background: Set stack and select ODS code for testing from the organisation dynamo table
    Given that the stack is "dos-search"
    Given there is an Organisation with an ODS code in the repo




  Scenario: I search for Organization endpoint data by ODS Code via APIM with an existing ODS code from the Organisation dynamo table
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"




  Scenario: I can access APIM for the dos-search 'ping' Endpoint and no access is required
    When I request data from the APIM endpoint "_ping" with an odscode from dynamo organisation table but without authentication
    Then I receive a status code "200" in response



  Scenario: I cannot search for Organization endpoint data by ODS Code without mtls credentials
    When I attempt to request data from the "dos-search" endpoint "Organization" with an odscode from dynamo organisation table but without authentication
    Then I receive a connection reset error




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with invalid access token
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with invalid token
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM without authentication
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but without authentication
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with malformed Authorization header format
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with malformed auth header
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding




  Scenario: I cannot search for Organization endpoint data by ODS Code via APIM with empty Authorization header
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table but with empty auth header
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding
