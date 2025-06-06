@is-api @is-pipeline @gp-search-api

Feature: API GP Endpoint Search
  Background: Set stack
    Given that the stack is "gp-search"

  Scenario: Search for GP Endpoint by ODS Code
    Given I request data for "odscode=M81046" from "organization"
    Then I receive a status code "422" in response
    And I receive the error code "INVALID_ODS_CODE_FORMAT"
    And I receive the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
    And I receive the diagnostics "Failed schema validation. Error: data must contain ['odsCode'] properties"
