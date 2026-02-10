@is-apim @integrated-search @dos-search-ods-code-api
@nhsd_apim_authorization(access="application",level="level3")
Feature: dos-search tests against the api-gateway and apim to validate the security of the endpoints

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario: I can access APIM for the dos-search'ping' Endpoint and no access is required
    When I request data from the APIM endpoint "_ping" with query params "" without authentication
    Then I receive a status code "200" in response


  Scenario: I can access APIM for the dos-search 'status' Endpoint and access is required
    When I request data from the APIM endpoint "_status" with query params "" with status token
    Then I receive a status code "200" in response


  Scenario: I can send a request to the dos-search api-gateway organisation endpoint with valid mtls credentials
    When I request data from the "dos-search" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources
    And the response is valid against the dos-search schema for endpoint "/Organization"

  Scenario: I cannot send a request to the dos-search api-gateway organisation endpoint without mtls credentials
    When I attempt to request data from the "dos-search" endpoint "Organization" without authentication but with valid query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M000081046"
    Then I receive a connection reset error

  Scenario: I can search APIM for the dos-search organization endpoint by ODS Code with valid query parameters and a valid access token
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


  Scenario: I cannot search APIM for the dos-search organization endpoint with invalid access token
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046" with invalid token
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding

  Scenario: I cannot search APIM for the dos-search organization endpoint without authentication
    When I request data from the APIM endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046" without authentication
    Then I receive a status code "401" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "security"
    And the OperationOutcome contains an issue with diagnostics "Invalid or missing authentication token"
    And the OperationOutcome contains an issue with details for INVALID_AUTH_CODING coding


