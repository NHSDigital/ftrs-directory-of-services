@is-api @is-pipeline @gp-search-api

Feature: API GP Endpoint Search
  Background: Set stack
    Given that the stack is "gp-search"


  Scenario: I search for GP Endpoint by ODS Code with valid query parameters
    Given I request data from the "servicesearch" endpoint "organization" with query params "_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M81046"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "1" "Organization" resources
    And the bundle contains "4" "Endpoint" resources

  Scenario Outline: I search for GP Endpoint with invalid parameters
    Given I request data from the "servicesearch" endpoint "organization" with query params "<params>"
    Then I receive a status code "502" in response
    And the response body contains JSON with a key "message" and value "Internal server error"

    Examples:
      | params                                    |
      | identifier=odsOrganisationCode\|M81046    |
      | _revinclude=Endpoint:organization         |
      |                                           |
      | identifier=                               |
      | _revinclude=                              |
      | _revinclude=invalid                       |
      | _revinclude=Endpoint:                     |


  Scenario Outline: I search for GP Endpoint with invalid ODS code
    Given I request data from the "servicesearch" endpoint "organization" with query params "<params>"
    Then I receive a status code "422" in response
    And the response body contains an "OperationOutcome" resource
    And the resource has an id of "ods-code-validation-error"

    Examples:
      | params                                    |
      | identifier=invalid                        |
      | identifier=odsOrganisationCode\|          |
      | identifier=\|M81046                       |
      | identifier=wrongSystem\|M81046            |
