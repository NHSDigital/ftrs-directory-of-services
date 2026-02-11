@is-smoke @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: dos-search smoke tests against the apim proxy

  Background: Retrieve an ods code from the Orgnisation dynamo table
  Given there is an Organisation with an ODS code in the repo


  Scenario: I send a request to the dos-search organization endpoint by ODS Code via APIM with an existing
    When I request data from the APIM endpoint "Organization" with an odscode from dynamo organisation table
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"


  Scenario: I can access APIM for the dos-search'ping' Endpoint and no access is required
    When I request data from the APIM endpoint "_ping" with query params "" without authentication
    Then I receive a status code "200" in response


  Scenario: I can access APIM for the dos-search 'status' Endpoint and access is required
    When I request data from the APIM endpoint "_status" with query params "" with status token
    Then I receive a status code "200" in response


  Scenario: I cannot search APIM for the dos-search organization endpoint with invalid access token
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|G83031" with invalid token
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding
    And the response is valid against the dos-search schema for endpoint "/Organization"

  Scenario: I cannot search APIM for the dos-search organization endpoint without authentication
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|G83031" without authentication
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding
