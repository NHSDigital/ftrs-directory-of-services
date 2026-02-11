@is-api @integrated-search @dos-search-ods-code-api
Feature: dos-search tests against the api-gateway to validate error handling

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario:I send a request to the dos-search organization endpoint for a endpoint that does not exist and the api-gateway returns a 404 error
    When I request data from the "dos-search" endpoint "DoesNotExist" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M000081046"
    Then I receive a status code "404" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "not-supported"
    And the OperationOutcome contains an issue with diagnostics "Unsupported service: /DoesNotExist"
    And the OperationOutcome contains an issue with details for UNSUPPORTED_SERVICE coding

