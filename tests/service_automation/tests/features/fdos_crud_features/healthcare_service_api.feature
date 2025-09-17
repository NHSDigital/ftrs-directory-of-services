@fdos-healthcare-service-api @is-pipeline
Feature: API tests for fdos Healthcare resources


  Scenario: Retrieve healthcare-service
    When I request data from the "crud" endpoint "healthcare-service/"
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "healthcare-service" resources



