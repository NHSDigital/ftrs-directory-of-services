@fdos-location-api @is-pipeline
Feature: API tests for Fdos Location resources


  Scenario: Retrieve Location resources
    When I request data from the "crud" endpoint "location/"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "location" resources



