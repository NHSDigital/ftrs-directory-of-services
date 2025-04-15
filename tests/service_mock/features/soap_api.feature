Feature: SOAP API Testing

  Scenario: Call the SOAP service
    Given the SOAP API is running
    When I send a SOAP request
    Then the response should contain "Hello SOAP User"
