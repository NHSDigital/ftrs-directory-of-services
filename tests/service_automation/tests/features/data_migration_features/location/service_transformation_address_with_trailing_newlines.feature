@data-migration
Feature: Service Transformation with Address and County
  As a test author
  I want to execute a data migration for an service transformation with Address and County
  So that I can confirm the migration process accurately transforms and transfers the service data without errors

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Migrate a single GP practice service
    Given a 'Service' exists called 'TestGPPractice' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 900090                                     |
      | uid                 | 200000                                     |
      | name                | TestGPPractice                             |
      | publicname          | The Village Surgery - Westminster Branch   |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12345                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | ME12 1HH                                    |
      | address             | Sheppey Healthy Living Centre Dr Shah$Royal Road, Off the Broadway, $Sheerness, $Kent $$  |
      | town                | SHEERNESS                                    |
      | web                 | https://www.nhs.uk/                        |
      | email               | england.contactus@nhs.net                  |
      | publicphone         | 0300 311 22 33                             |
    When a single service migration is run for ID '900090'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '900090' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the service has the address
    And the service address for ID '900090' should be:
      | key      | value                    |
      | county   | Kent                  |
      | line1    | Sheppey Healthy Living Centre Dr Shah  |
      | line2    | Royal Road, Off the Broadway,               |
      | postcode | ME12 1HH                  |
      | town     | SHEERNESS             |
