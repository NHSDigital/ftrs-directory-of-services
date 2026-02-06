@is-api @ftrs-pipeline @dos-search-ods-code-api
Feature: API DoS Service Search Backend Gateway Errors
# Feature: Dos-search api tests against the api-gateway to validate the error catching

  Background: Set stack and seed repo
    Given that the stack is "dos-search"
    And the dns for "dos-search" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"

@test
  Scenario: I send a request to the api-gateway with missing mtls cert and key
    When I request data from the "dos-search" endpoint "Organization" without authentication but with valid query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M000081046"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter '<missing_param>'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                    | missing_param |
      | identifier=odsOrganisationCode\|M00081046 | _revinclude   |
      | _revinclude=Endpoint:organization         | identifier    |

