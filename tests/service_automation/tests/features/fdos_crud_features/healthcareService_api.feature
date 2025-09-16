@fdos-org-api @is-pipeline
Feature: API tests for Fdos Healthcare resources


  Scenario: Retrieve HealthcareService resources
    When I request data from the "crud" endpoint "healthcare-service" with a "GET" method
    Then I receive a status code "200" in response
    And the response body contains a bundle
    And the bundle contains "10" "healthcare-service" resources



