@is-api @manual @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: API DoS Service Search APIM

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario: I can access APIM for the 'ping' Endpoint and no access is required
    When I request data from the APIM "dos-search" endpoint "_ping" with "" query params and "no" access token
    Then I receive a status code "200" in response

# Waiting for dosis-1893 to be done
  # Scenario: I can access APIM for the 'status' Endpoint and access is required
  #   When I request data from the APIM "dos-search" endpoint "_status" with "" query params and "valid" access token
  #   Then I receive a status code "200" in response


  Scenario: I search APIM for GP Endpoint by ODS Code with valid query parameters and a valid access token
    When I request data from the APIM "dos-search" endpoint "Organization" with "valid" query params and "valid" access token
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


  Scenario Outline: I search APIM for GP Endpoint without a valid access token
    When I request data from the APIM "dos-search" endpoint "Organization" with "valid" query params and "<token_type>" access token
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding
    Examples:
      | token_type |
      | invalid    |
      | missing    |


