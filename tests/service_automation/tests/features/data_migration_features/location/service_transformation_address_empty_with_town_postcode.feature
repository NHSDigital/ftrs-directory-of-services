@data-migration
Feature: Service Transformation with Empty Address but Town/Postcode Present
  As a test author
  I want to execute a data migration for services with empty address but populated town or postcode
  So that I can confirm validation errors are raised as expected per data quality rules

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Attempt to migrate GP practice with empty address but town and postcode present
    Given a 'Service' exists called 'TestGPEmptyAddress1' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24180                                      |
      | uid                 | 200040                                     |
      | name                | TestGPEmptyAddress1                        |
      | publicname          | Test Surgery - Empty Address 1             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12360                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SO1 1AA                                    |
      | address             |                                            |
      | town                | Southampton                                |
      | web                 | https://www.nhs.uk/                        |
      | email               | test1@nhs.net                              |
      | publicphone         | 0300 111 22 40                             |
    When a single service migration is run for ID '24180'
    Then the service should have a validation error with code 'address_required'

  Scenario: Attempt to migrate GP practice with empty address but only postcode present
    Given a 'Service' exists called 'TestGPEmptyAddress2' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24181                                      |
      | uid                 | 200041                                     |
      | name                | TestGPEmptyAddress2                        |
      | publicname          | Test Surgery - Empty Address 2             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12361                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SO1 1AA                                    |
      | address             |                                            |
      | town                |                                            |
      | web                 | https://www.nhs.uk/                        |
      | email               | test2@nhs.net                              |
      | publicphone         | 0300 111 22 41                             |
    When a single service migration is run for ID '24181'
    Then the service should have a validation error with code 'address_required'

  Scenario: Attempt to migrate GP practice with empty address but only town present
    Given a 'Service' exists called 'TestGPEmptyAddress3' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24182                                      |
      | uid                 | 200042                                     |
      | name                | TestGPEmptyAddress3                        |
      | publicname          | Test Surgery - Empty Address 3             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12362                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            |                                            |
      | address             |                                            |
      | town                | Southampton                                |
      | web                 | https://www.nhs.uk/                        |
      | email               | test3@nhs.net                              |
      | publicphone         | 0300 111 22 42                             |
    When a single service migration is run for ID '24182'
    Then the service should have a validation error with code 'address_required'

  Scenario: Attempt to migrate GP practice with all address fields empty
    Given a 'Service' exists called 'TestGPEmptyAddress4' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24183                                      |
      | uid                 | 200043                                     |
      | name                | TestGPEmptyAddress4                        |
      | publicname          | Test Surgery - Empty Address 4             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12363                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            |                                            |
      | address             |                                            |
      | town                |                                            |
      | web                 | https://www.nhs.uk/                        |
      | email               | test4@nhs.net                              |
      | publicphone         | 0300 111 22 43                             |
    When a single service migration is run for ID '24183'
    Then the service should have a validation error with code 'address_required'
