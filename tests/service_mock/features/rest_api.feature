Feature: REST API Testing

  Scenario: Get a user from the REST API
    Given the REST API is running
    When I send a GET request to "/api/user/1"
    Then the response status code should be 200
    And the response should contain "John Doe"
