@data-migration
Feature: Data Migration - GP Practice with Feature Flag Disabled

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: GP Practice migration when DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED is disabled
    Given the feature flag 'DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED' is set to 'false'
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                                                                                                                                                                                                   |
      | id                                  | 10005752                                                                                                                                                                                                                                |
      | uid                                 | 138179                                                                                                                                                                                                                                  |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire                                                                                                                                                                                         |
      | odscode                             | M81094                                                                                                                                                                                                                                  |
      | openallhours                        | FALSE                                                                                                                                                                                                                                   |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752                                                                                                                                                                                        |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752                                                                                                                                                                             |
      | restricttoreferrals                 | TRUE                                                                                                                                                                                                                                    |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                                                                                                                                                                                               |
      | town                                | EVESHAM                                                                                                                                                                                                                                 |
      | postcode                            | WR11 4BS                                                                                                                                                                                                                                |
      | easting                             | 403453                                                                                                                                                                                                                                  |
      | northing                            | 243634                                                                                                                                                                                                                                  |
      | publicphone                         | 01386 761111                                                                                                                                                                                                                            |
      | nonpublicphone                      | 99999 000000                                                                                                                                                                                                                            |
      | fax                                 | 77777 000000                                                                                                                                                                                                                            |
      | email                               |                                                                                                                                                                                                                                         |
      | web                                 | www.abbeymedical.com                                                                                                                                                                                                                    |
      | createdby                           | HUMAN                                                                                                                                                                                                                                   |
      | createdtime                         | 2011-06-29 08:00:51.000                                                                                                                                                                                                                 |
      | modifiedby                          | HUMAN                                                                                                                                                                                                                                   |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                                                                                                                                                                                                 |
      | lasttemplatename                    | Midlands template R46 Append PC                                                                                                                                                                                                         |
      | lasttemplateid                      | 244764                                                                                                                                                                                                                                  |
      | typeid                              | 100                                                                                                                                                                                                                                     |
      | parentid                            | 150013                                                                                                                                                                                                                                  |
      | subregionid                         | 150013                                                                                                                                                                                                                                  |
      | statusid                            | 1                                                                                                                                                                                                                                       |
      | organisationid                      |                                                                                                                                                                                                                                         |
      | returnifopenminutes                 |                                                                                                                                                                                                                                         |
      | publicname                          | O&#39;Reilly Medical Practice &#38; Sons                                                                                                                                                                                                   |
      | latitude                            | 52.0910543                                                                                                                                                                                                                              |
      | longitude                           | -1.951003                                                                                                                                                                                                                               |
      | professionalreferralinfo            | Non-public numbers are for healthcare professionals ONLY; they are not for routine contact and must not be shared with patients\n* GP practice opening hours are 08:00-18:30, hours shown on DoS may vary for administration purposes." |
      | lastverified                        |                                                                                                                                                                                                                                         |
      | nextverificationdue                 |                                                                                                                                                                                                                                         |

    When the data migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 0 location and 0 healthcare services created
    Then the state table contains a record for key 'services#10005752' with version 1
    Then the state table contains 2 validation issue(s) for key 'services#10005752'
    Then the state table contains the following validation issues for key 'services#10005752':
      | expression     | code             | severity | diagnostics             | value       |
      | email          | email_not_string | error    | Email must be a string  | None        |
      | nonpublicphone | invalid_format   | error    | Phone number is invalid | 99999000000 |

    Then the 'organisation' for service ID '10005752' has content:
      """
      {
        "id": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "identifier_oldDoS_uid": "138179",
        "field": "document",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "2025-10-07T08:38:57.679754Z",
        "endpoints": [],
        "identifier_ODS_ODSCode": "M81094",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "2025-10-07T08:38:57.679754Z",
        "name": "O'Reilly Medical Practice & Sons",
        "telecom": [],
        "type": "GP Practice",
        "legalDates": null,
        "primary_role_code": null,
        "non_primary_role_codes": []
      }
      """
