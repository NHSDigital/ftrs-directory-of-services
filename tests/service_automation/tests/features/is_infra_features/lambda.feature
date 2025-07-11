@is-infra @is-pipeline @is-lambda
Feature: Lambda function

Background: Check lambda function exists
  Given that the lambda function "gp-search-lambda" exists for stack "gp-search"


  Scenario: The lambda returns a response that contains the ods code
  When I invoke the lambda with the ods code "M81046"
  Then the lambda response contains the ods code "M81046"
  And the lambda response contains the endpoint id "b1578130-52ee-4eeb-9458-e676f55e1a0b"


#-------------------schema and structure tests-------------------

  Scenario: The lambda returns a valid response against the schema
  When I invoke the lambda with the ods code "M81046"
  Then the lambda response contains a bundle
  And the lambda response contains "1" "Organization" resources
  And the lambda response contains "4" "Endpoint" resources

  Scenario: The Lambda response contains a bundle
  When I invoke the lambda with the ods code "N81063"
  Then the lambda response contains a bundle


  Scenario: The Lambda response contains an organization resource
  When I invoke the lambda with the ods code "N81063"
  Then the lambda response contains "1" "Organization" resources

  Scenario: The Lambda response contains an endpoint resource
  When I invoke the lambda with the ods code "N81063"
  Then the lambda response contains "4" "Endpoint" resources


  Scenario: For an odsCode without Endpoints a bundle containing only an organisazation resource will be returned
  When I invoke the lambda with the ods code "F81015"
  Then the lambda response contains "0" "Endpoint" resources

  Scenario: For an odsCode that has more than one record only the first record will be returned
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains the ods code "P83010"
  And the lambda response contains "1" "Organization" resources
  And the lambda response contains "2" "Endpoint" resources


  Scenario: For an odsCode that does not exist an empty bundle will be returned
  When I invoke the lambda with the ods code "12345"
  Then the lambda response contains an empty bundle


  Scenario: A lowercase odscode is accepted and returns a response for the same odsCode
  When I invoke the lambda with the ods code "p83010"
  Then the lambda response contains the ods code "P83010"

#-------------------validation tests------------------


  Scenario: Invoke lambda with an ods code of a length of 12 and a valid response is returned
  When I invoke the lambda with the ods code "abcdefGHIJ12"
  Then the lambda response contains the ods code "abcdefGHIJ12"


  Scenario: Invoke lambda with an ods code of a length of 5 and a valid response is returned
  When I invoke the lambda with the ods code "E8104"
  Then the lambda response contains the ods code "E8104"

    Scenario: The Lambda response contains a bundle
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains a bundle

  Scenario: Invoke lambda with an ods code set to "" and a validation error is returned
  When I invoke the lambda with the ods code ""
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Value error, ODS code must be at least 5 characters long"


  Scenario: Invoke lambda with an ods code of a length of 13 and a validation error is returned
  When I invoke the lambda with the ods code "ABCDEFGHIJKLM"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Value error, ODS code must be at most 12 characters long"


  Scenario: Invoke lambda with an ods code of a length of 4 and a validation error is returned
  When I invoke the lambda with the ods code "ABCD"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Value error, ODS code must be at least 5 characters long"


  Scenario: Invoke lambda with an ods code containing special characters and a validation error is returned
  When I invoke the lambda with the ods code "P83010@"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Value error, ODS code must contain only letters and numbers"

