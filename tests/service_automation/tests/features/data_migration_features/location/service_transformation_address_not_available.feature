@data-migration
Feature: Service Transformation with "Not Available" Address
  As a test author
  I want to execute a data migration for services with "Not Available" address values
  So that I can confirm these cases are handled correctly without errors

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Migrate GP practice with exact "Not Available" address
    Given a 'Service' exists called 'TestGPNotAvailable1' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24170                                      |
      | uid                 | 200030                                     |
      | name                | TestGPNotAvailable1                        |
      | publicname          | Test Surgery - Not Available 1             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12350                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | W1A 1AA                                    |
      | address             | Not Available                              |
      | town                | London                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | test1@nhs.net                              |
      | publicphone         | 0300 111 22 33                             |
    When a single service migration is run for ID '24170'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '24170' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the location for service ID '24170' should have no address

  Scenario: Migrate GP practice with lowercase "not available" address
    Given a 'Service' exists called 'TestGPNotAvailable2' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24171                                      |
      | uid                 | 200031                                     |
      | name                | TestGPNotAvailable2                        |
      | publicname          | Test Surgery - Not Available 2             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12351                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | W1A 1AA                                    |
      | address             | not available                              |
      | town                | London                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | test2@nhs.net                              |
      | publicphone         | 0300 111 22 34                             |
    When a single service migration is run for ID '24171'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '24171' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the location for service ID '24171' should have no address

  Scenario: Migrate GP practice with uppercase "NOT AVAILABLE" address
    Given a 'Service' exists called 'TestGPNotAvailable3' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24172                                      |
      | uid                 | 200032                                     |
      | name                | TestGPNotAvailable3                        |
      | publicname          | Test Surgery - Not Available 3             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12352                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            |                                            |
      | address             | NOT AVAILABLE                              |
      | town                |                                            |
      | web                 | https://www.nhs.uk/                        |
      | email               | test3@nhs.net                              |
      | publicphone         | 0300 111 22 35                             |
    When a single service migration is run for ID '24172'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '24172' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the location for service ID '24172' should have no address

  Scenario: Migrate GP practice with mixed case "NoT aVaIlAbLe" address
    Given a 'Service' exists called 'TestGPNotAvailable4' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24173                                      |
      | uid                 | 200033                                     |
      | name                | TestGPNotAvailable4                        |
      | publicname          | Test Surgery - Not Available 4             |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12353                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SE1 1AA                                    |
      | address             | NoT aVaIlAbLe                              |
      | town                | LONDON                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | test4@nhs.net                              |
      | publicphone         | 0300 111 22 36                             |
    When a single service migration is run for ID '24173'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And service ID '24173' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the location for service ID '24173' should have no address
