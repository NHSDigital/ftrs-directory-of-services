@is-infra @is-pipeline
Feature: Lambda function

Background: Check lambda function exists
  Given that the lambda function "gp-search-lambda" exists for stack "gp-search"


  Scenario: Invoke lambda
  When I invoke the lambda with the ods code "P83010"
  Then the lambda response contains the ods code "P83010"


  Scenario: Invoke lambda with ods code that does not exist
  When I invoke the lambda with the ods code "12345"
  Then the lambda response contains an empty bundle

  @is-lambda
  Scenario: Invoke lambda with empty ods code
  When I invoke the lambda with an empty ods code
  Then the lambda returns the error message "Internal server error while processing ODS code ''" with status code "500"

  Scenario: Invoke lambda with ods code for organisation with no endpoints
  When I invoke the lambda with the ods code "F81015"
  Then the lambda response contains the ods code "P83010"
