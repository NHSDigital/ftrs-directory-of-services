@is-infra @is-pipeline @is-lambda
Feature: Lambda function

Background: Check lambda function exists
  Given that the lambda function "gp-search-lambda" exists for stack "gp-search"


  Scenario: Invoke lambda
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains the ods code "P83010"


  Scenario: Invoke lambda returns a valid response
  When I invoke the lambda with the ods code "F81015"
  Then the response is valid against the schema

  Scenario: Invoke lambda with a lowercase ods code
  When I invoke the lambda with the ods code "p83010"
  Then the lambda response contains the ods code "P83010"


  Scenario: Invoke lambda with an ods code that does not exist
  When I invoke the lambda with the ods code "12345"
  Then the lambda response contains an empty bundle

  Scenario: Invoke lambda with an empty ods code
  When I invoke the lambda with the ods code value not set
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be longer than or equal to 5 characters, Path: ['data', 'odsCode'], Data: "


  Scenario: Invoke lambda with an ods code of a length of 13
  When I invoke the lambda with the ods code "ABCDEFGHIJKLM"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be shorter than or equal to 12 characters, Path: ['data', 'odsCode'], Data: ABCDEFGHIJKLM"

  Scenario: Invoke lambda with an ods code of a length of 4
  When I invoke the lambda with the ods code "ABCD"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must be longer than or equal to 5 characters, Path: ['data', 'odsCode'], Data: ABCD"


  Scenario: Invoke lambda with an ods code containing special characters
  When I invoke the lambda with the ods code "P83010@"
  Then the lambda returns the status code "422"
  And the lambda returns the error code "INVALID_ODS_CODE_FORMAT"
  And the lambda returns the message "The organization.identifier ODS code provided in the search parameter does not match the required format"
  And the lambda returns the diagnostics "Failed schema validation. Error: data.odsCode must match pattern ^[A-Z0-9]+$, Path: ['data', 'odsCode'], Data: P83010@"


  Scenario: Invoke lambda with an ods code for an organisation with no endpoints
  When I invoke the lambda with the ods code "F81015"
  Then the lambda response does not contain an endpoint resource
