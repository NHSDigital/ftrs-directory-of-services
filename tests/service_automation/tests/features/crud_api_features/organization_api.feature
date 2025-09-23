@crud-org-api @is-pipeline
Feature: API tests for Fdos Organization resource including linked Endpoint resources


  Scenario: Retrieve Organization
    When I request data from the "crud" endpoint "Organization"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "Organization" resources



