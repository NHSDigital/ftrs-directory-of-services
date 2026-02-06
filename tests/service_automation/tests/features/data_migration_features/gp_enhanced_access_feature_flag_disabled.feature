@data-migration
Feature: Data Migration - GP Enhanced Access with Feature Flag Disabled

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: GP Enhanced Access migration when DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED is disabled
    Given the feature flag 'DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED' is set to 'false'
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                         |
      | id                                  | 100178970                                                     |
      | uid                                 | 2000094797                                                    |
      | name                                | PCN - Enhanced Access Hub, Sandwell                           |
      | odscode                             | U31548                                                        |
      | isnational                          |                                                               |
      | openallhours                        | FALSE                                                         |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 178970            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 178970 |
      | restricttoreferrals                 | TRUE                                                          |
      | address                             | Postcode for lookup purpose only                              |
      | town                                | WEDNESBURY                                                    |
      | postcode                            | WS10 0JS                                                      |
      | easting                             | 400927                                                        |
      | northing                            | 295144                                                        |
      | publicphone                         |                                                               |
      | nonpublicphone                      | 99999 000000                                                  |
      | fax                                 |                                                               |
      | email                               | 178970-fake@nhs.gov.uk                                        |
      | web                                 |                                                               |
      | createdby                           | HUMAN                                                         |
      | createdtime                         | 2022-02-11 15:36:15.000                                       |
      | modifiedby                          | HUMAN                                                         |
      | modifiedtime                        | 2025-02-14 11:47:40.000                                       |
      | lasttemplatename                    | PCN - Enhanced Access Hub, Sandwell                           |
      | lasttemplateid                      | 246421                                                        |
      | typeid                              | 152                                                           |
      | parentid                            | 162870                                                        |
      | subregionid                         | 98096                                                         |
      | statusid                            | 1                                                             |
      | organisationid                      |                                                               |
      | returnifopenminutes                 |                                                               |
      | publicname                          | PCN - Enhanced Access Hub, Sandwell                           |
      | latitude                            | 52.5541526                                                    |
      | longitude                           | -1.9877538                                                    |
      | professionalreferralinfo            |                                                               |
      | lastverified                        |                                                               |
      | nextverificationdue                 |                                                               |

    When the data migration process is run for table 'services', ID '100178970' and method 'insert'
    Then the SQS event metrics should be 1 total, 0 supported, 1 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 0 organisation, 0 location and 0 healthcare services created
