@is-infra @is-pipeline
Feature: Lambda function

Background: Check lambda function exists
  Given that the lambda function "gp-search-lambda" exists for stack "gp-search"

  Scenario: Invoke lambda
  When I invoke the lambda
  Then the lambda response contains the odscode "P83010"
