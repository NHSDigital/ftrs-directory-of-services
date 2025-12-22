@data-migration
Feature: Service Transformation with Empty Address but Town/Postcode Present
  As a test author
  I want to execute a data migration for services with empty address but populated town or postcode
  So that I can confirm validation errors are raised as expected per data quality rules

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario Outline: Attempt to migrate GP practice with empty address (<scenario_description>)
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                      |
      | id                  | <service_id>               |
      | uid                 | <uid>                      |
      | name                | <service_name>             |
      | publicname          | <publicname>               |
      | typeid              | 100                        |
      | statusid            | 1                          |
      | odscode             | <odscode>                  |
      | createdtime         | 2024-01-01 10:00:00        |
      | modifiedtime        | 2024-01-01 10:00:00        |
      | openallhours        | false                      |
      | restricttoreferrals | false                      |
      | postcode            | <postcode>                 |
      | address             |                            |
      | town                | <town>                     |
      | web                 | https://www.nhs.uk/        |
      | email               | <email>                    |
      | publicphone         | <publicphone>              |
    When a single service migration is run for ID '<service_id>'
    Then the service should have a validation error with code 'address_required'

    Examples:
      | scenario_description         | service_id | uid    | service_name        | publicname                  | odscode | town        | postcode | email         | publicphone    |
      | town and postcode present    | 24180      | 200040 | TestGPEmptyAddress1 | Test Surgery - Empty Address 1 | B12360  | Southampton | SO1 1AA  | test1@nhs.net | 0300 111 22 40 |
      | only postcode present        | 24181      | 200041 | TestGPEmptyAddress2 | Test Surgery - Empty Address 2 | B12361  |             | SO1 1AA  | test2@nhs.net | 0300 111 22 41 |
      | only town present            | 24182      | 200042 | TestGPEmptyAddress3 | Test Surgery - Empty Address 3 | B12362  | Southampton |          | test3@nhs.net | 0300 111 22 42 |
      | all address fields empty     | 24183      | 200043 | TestGPEmptyAddress4 | Test Surgery - Empty Address 4 | B12363  |             |          | test4@nhs.net | 0300 111 22 43 |
