@data-migration
Feature: Data Migration - Community Pharmacy with Feature Flag Disabled

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Community Pharmacy migration when DATA_MIGRATION_PHARMACY_ENABLED is disabled
    Given the feature flag 'DATA_MIGRATION_PHARMACY_ENABLED' is set to 'false'
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 10012347                                                 |
      | uid                                 | 999997                                                   |
      | name                                | Test Community Pharmacy Flag Disabled                    |
      | odscode                             | FXX97                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field              |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text         |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 789 Flag Test Street$Test Area$Test City                 |
      | town                                | TESTTOWN                                                 |
      | postcode                            | TE2 2ST                                                  |
      | easting                             | 403453                                                   |
      | northing                            | 243634                                                   |
      | publicphone                         | 01234 567890                                             |
      | nonpublicphone                      | 09876 543210                                             |
      | fax                                 |                                                          |
      | email                               | flagtest.pharmacy@nhs.net                                |
      | web                                 | www.flagtestpharmacy.com                                 |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2020-01-15 08:00:51.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                  |
      | lasttemplatename                    | Pharmacy Template                                        |
      | lasttemplateid                      | 244764                                                   |
      | typeid                              | 13                                                       |
      | parentid                            | 150013                                                   |
      | subregionid                         | 150013                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Test Community Pharmacy Flag Disabled                    |
      | latitude                            | 52.0910543                                               |
      | longitude                           | -1.951003                                                |
      | professionalreferralinfo            | Professional referral information                        |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '10012347' and method 'insert'
    Then the SQS event metrics should be 1 total, 0 supported, 1 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 0 organisation, 0 location and 0 healthcare services created
