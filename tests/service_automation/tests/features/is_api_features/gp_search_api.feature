@is-api @is-pipeline @gp-search-api
Feature: API GP Endpoint Search

  Background: Set stack and seed repo
    Given that the stack is "gp-search"
    And the dns for "servicesearch" is resolvable
    And I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"


  Scenario: I search for GP Endpoint by ODS Code with valid query parameters
    When I request data from the "servicesearch" endpoint "Organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M00081046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources


  Scenario Outline: I search for GP Endpoint with invalid ODS code
    When I request data from the "servicesearch" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier value: ODS code '<ods_code>' must follow format ^[A-Za-z0-9]{5,12}$"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                          | ods_code      |
      | identifier=odsOrganisationCode\|&_revinclude=Endpoint:organization              |               |
      | identifier=odsOrganisationCode\|0123&_revinclude=Endpoint:organization          | 0123          |
      | identifier=odsOrganisationCode\|0123456789ABC&_revinclude=Endpoint:organization | 0123456789ABC |
      | identifier=odsOrganisationCode\|123@@@&_revinclude=Endpoint:organization        | 123@@@        |


  Scenario Outline: I search for GP Endpoint with invalid _revinclude value
    When I request data from the "servicesearch" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "value"
    And the OperationOutcome contains an issue with diagnostics "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                      |
      | identifier=odsOrganisationCode\|M00081046&_revinclude=                      |
      | identifier=odsOrganisationCode\|M00081046&_revinclude=Invalid:value         |
      | identifier=odsOrganisationCode\|M00081046&_revinclude=ENDPOINT:ORGANIZATION |


  Scenario Outline: I search for GP Endpoint with invalid identifier system
    When I request data from the "servicesearch" endpoint "Organization" with query params "<params>"
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "1" issues
    And the OperationOutcome contains an issue with severity "error"
    And the OperationOutcome contains an issue with code "code-invalid"
    And the OperationOutcome contains an issue with diagnostics "Invalid identifier system '<identifier_system>' - expected 'odsOrganisationCode'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
    Examples:
      | params                                                                             | identifier_system          |
      | identifier=\|M00081046&_revinclude=Endpoint:organization                           |                            |
      | identifier=invalidSystem\|M00081046&_revinclude=Endpoint:organization              | invalidSystem              |
      | identifier=odsOrganisationCodeInvalid\|M00081046&_revinclude=Endpoint:organization | odsOrganisationCodeInvalid |


  Scenario Outline: I search for GP Endpoint with 1 missing parameter
    When I request data from the "servicesearch" endpoint "Organization" with query params "<params>"
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


  Scenario: I search for GP Endpoint with 2 missing parameters
    When I request data from the "servicesearch" endpoint "Organization" with query params ""
    Then I receive a status code "400" in response
    And the response body contains an "OperationOutcome" resource
    And the OperationOutcome contains "2" issues
    And the OperationOutcome has issues all with severity "error"
    And the OperationOutcome has issues all with code "required"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter 'identifier'"
    And the OperationOutcome contains an issue with diagnostics "Missing required search parameter '_revinclude'"
    And the OperationOutcome contains an issue with details for INVALID_SEARCH_DATA coding
