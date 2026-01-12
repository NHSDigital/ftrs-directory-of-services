@data-migration
Feature: Service Transformation with Address and County

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Migrate a single GP practice service
    Given a 'Service' exists called 'TestGPPractice' in DoS with attributes:
      | key                 | value                                                                                  |
      | id                  | 24165                                                                                  |
      | uid                 | 200023                                                                                 |
      | name                | TestGPPractice                                                                         |
      | publicname          | The Village Surgery - Westminster Branch                                               |
      | typeid              | 100                                                                                    |
      | statusid            | 1                                                                                      |
      | odscode             | B12345                                                                                 |
      | createdtime         | 2024-01-01 10:00:00                                                                    |
      | modifiedtime        | 2024-01-01 10:00:00                                                                    |
      | openallhours        | false                                                                                  |
      | restricttoreferrals | false                                                                                  |
      | postcode            | HA8 0AD                                                                                |
      | address             | Zain Medical Centre$Edgware Community Hospital$Outpatient D$Burnt Oak Broadway$Edgware |
      | town                | EDGWARE                                                                                |
      | web                 | https://www.nhs.uk/                                                                    |
      | email               | england.contactus@nhs.net                                                              |
      | publicphone         | 0300 311 22 33                                                                         |
    When a single service migration is run for ID '24165'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errors
    And service ID '24165' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the service has the address
    And the service address for ID '24165' should be:
      | key      | value                      |
      | county   | None                       |
      | line1    | Zain Medical Centre        |
      | line2    | Edgware Community Hospital |
      | postcode | HA8 0AD                    |
      | town     | EDGWARE                    |

  Scenario: Migrate GP practice with county in middle of address (not at end)
    Given a 'Service' exists called 'TestGPPracticeCountyMiddle' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 24166                                      |
      | uid                 | 200024                                     |
      | name                | TestGPPracticeCountyMiddle                 |
      | publicname          | Test Surgery - Middle County Branch        |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12346                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SO1 1AA                                    |
      | address             | 123 Main Street$Building A$Hampshire$Extra Line$More Data |
      | town                | Southampton                                |
      | web                 | https://www.nhs.uk/                        |
      | email               | test@nhs.net                               |
      | publicphone         | 0300 111 22 33                             |
    When a single service migration is run for ID '24166'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And service ID '24166' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the service has the address
    And the service address for ID '24166' should be:
      | key      | value                    |
      | county   | Hampshire                |
      | line1    | 123 Main Street          |
      | line2    | Building A               |
      | postcode | SO1 1AA                  |
      | town     | Southampton              |
