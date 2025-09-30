@apim-test
Feature: APIM Security

  Scenario: Ping endpoint should be healthy
    When I send a GET request to the "health" endpoint
    Then I receive a status code "200" in response

  Scenario: Status endpoint is secured
    When I send a GET request to the "status" endpoint without authentication
    Then I receive a status code "401" in response

  Scenario: Organization endpoint is secured
    When I send a PUT request to the "organization" endpoint without authentication
    Then I receive a status code "401" in response

  Scenario: Organization endpoint with invalid API key
    When I send a PUT request to the "organization" endpoint with invalid API key "invalidkey232342"
    Then I receive a status code "401" in response
