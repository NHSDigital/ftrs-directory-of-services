@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Happy path migration for a GP Practice
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
      | publicname                          | Abbey Medical Practice                                                                                                                                                                                                                  |
      | latitude                            | 52.0910543                                                                                                                                                                                                                              |
      | longitude                           | -1.951003                                                                                                                                                                                                                               |
      | professionalreferralinfo            | Non-public numbers are for healthcare professionals ONLY; they are not for routine contact and must not be shared with patients\n* GP practice opening hours are 08:00-18:30, hours shown on DoS may vary for administration purposes." |
      | lastverified                        |                                                                                                                                                                                                                                         |
      | nextverificationdue                 |                                                                                                                                                                                                                                         |

    When the data migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
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
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-10-07T08:38:57.679754Z",
        "endpoints": [],
        "identifier_ODS_ODSCode": "M81094",
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-10-07T08:38:57.679754Z",
        "name": "Abbey Medical Practice",
        "telecom": [],
        "type": "GP Practice",
        "legalDates": null,
        "primary_role_code": null,
        "non_primary_role_codes": []
      }
      """
    Then the 'healthcare-service' for service ID '10005752' has content:
      """
      {
        "id": "48865e3d-b8f0-508b-8520-29b3113da1e3",
        "field": "document",
        "active": true,
        "ageEligibilityCriteria": null,
        "category": "GP Services",
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-10-07T08:38:57.679754Z",
        "dispositions": [],
        "identifier_oldDoS_uid": "138179",
        "location": "fbb2340b-53e0-56f9-ada3-ef5728ca8f98",
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-10-07T08:38:57.679754Z",
        "name": "Abbey Medical Practice, Evesham, Worcestershire",
        "openingTime": [],
        "providedBy": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "symptomGroupSymptomDiscriminators": [],
        "telecom": {
          "email": null,
          "phone_private": null,
          "phone_public": "01386761111",
          "web": "www.abbeymedical.com"
        },
        "type": "GP Consultation Service"
      }
      """
    Then the 'location' for service ID '10005752' has content:
      """
      {
        "id": "fbb2340b-53e0-56f9-ada3-ef5728ca8f98",
        "identifier_oldDoS_uid": "138179",
        "field": "document",
        "active": true,
        "address": {
          "county": null,
          "line1": "Evesham Medical Centre",
          "line2": "Abbey Lane",
          "postcode": "WR11 4BS",
          "town": "EVESHAM"
        },
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-11-13T15:39:53.539806Z",
        "managingOrganisation": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-11-13T15:39:53.539806Z",
        "name": null,
        "partOf": null,
        "positionGCS": {
          "latitude": "52.0910543000",
          "longitude": "-1.9510030000"
        },
        "positionReferenceNumber_UBRN": null,
        "positionReferenceNumber_UPRN": null,
        "primaryAddress": true
      }
      """

  @gp-name-truncation
  Scenario: GP practice names are truncated on " - " separator
    Given a "Service" exists in DoS with attributes
      | key                  | value                                   |
      | id                   | 10015752                                |
      | uid                  | 145771                                  |
      | name                 | Lockside Medical Centre - T+G           |
      | odscode              | A83001                                  |
      | openallhours         | FALSE                                   |
      | restricttoreferrals  | FALSE                                   |
      | address              | 123 Test Street                         |
      | town                 | TestTown                                |
      | postcode             | TE1 1ST                                 |
      | publicname           | Lockside Medical Centre - T+G           |
      | typeid               | 100                                     |
      | statusid             | 1                                       |
      | createdtime          | 2024-01-01 10:00:00                     |
      | modifiedtime         | 2024-01-01 10:00:00                     |

    And a "Service" exists in DoS with attributes
      | key                  | value                                        |
      | id                   | 10025752                                     |
      | uid                  | 112433                                       |
      | name                 | Abbey-Dale Medical Centre                    |
      | odscode              | A83002                                       |
      | openallhours         | FALSE                                        |
      | restricttoreferrals  | FALSE                                        |
      | address              | 456 Abbey Dale Road                          |
      | town                 | Sheffield                                    |
      | postcode             | S17 1AB                                      |
      | publicname           | Abbey-Dale Medical Centre                    |
      | typeid               | 100                                          |
      | statusid             | 1                                            |
      | createdtime          | 2024-01-01 10:00:00                          |
      | modifiedtime         | 2024-01-01 10:00:00                          |

    And a "Service" exists in DoS with attributes
      | key                  | value                                                |
      | id                   | 10035752                                             |
      | uid                  | 1336055953                                           |
      | name                 | GP - Nene Valley and Hodgson - Peterborough          |
      | odscode              | A83003                                               |
      | openallhours         | FALSE                                                |
      | restricttoreferrals  | FALSE                                                |
      | address              | Nene Valley Surgery                                  |
      | town                 | Peterborough                                         |
      | postcode             | PE1 1AA                                              |
      | publicname           | GP - Nene Valley and Hodgson - Peterborough          |
      | typeid               | 100                                                  |
      | statusid             | 1                                                    |
      | createdtime          | 2024-01-01 10:00:00                                  |
      | modifiedtime         | 2024-01-01 10:00:00                                  |

    When the data migration process is run for table 'services', ID '10015752' and method 'insert'
    And the data migration process is run for table 'services', ID '10025752' and method 'insert'
    And the data migration process is run for table 'services', ID '10035752' and method 'insert'
    Then there is 3 organisation, 3 location and 3 healthcare services created
    Then the organisation for service ID 10015752 has name Lockside Medical Centre
    Then the organisation for service ID 10025752 has name Abbey-Dale Medical Centre
    Then the organisation for service ID 10035752 has name Nene Valley and Hodgson

  @html-decoding
  Scenario: HTML-encoded characters are decoded in GP practice names
    Given a "Service" exists in DoS with attributes
      | key                  | value                                          |
      | id                   | 10045752                                       |
      | uid                  | 150001                                         |
      | name                 | St Peters Health Centre (Dr S&#39;Souza)       |
      | odscode              | A84001                                         |
      | openallhours         | FALSE                                          |
      | restricttoreferrals  | FALSE                                          |
      | address              | St Peters Road                                 |
      | town                 | Birmingham                                     |
      | postcode             | B1 1AA                                         |
      | publicname           | St Peters Health Centre (Dr S&#39;Souza)       |
      | typeid               | 100                                            |
      | statusid             | 1                                              |
      | createdtime          | 2024-01-01 10:00:00                            |
      | modifiedtime         | 2024-01-01 10:00:00                            |

    And a "Service" exists in DoS with attributes
      | key                  | value                                          |
      | id                   | 10055752                                       |
      | uid                  | 150002                                         |
      | name                 | The Surgery &amp; Medical Centre               |
      | odscode              | A84002                                         |
      | openallhours         | FALSE                                          |
      | restricttoreferrals  | FALSE                                          |
      | address              | High Street                                    |
      | town                 | Manchester                                     |
      | postcode             | M1 1AA                                         |
      | publicname           | The Surgery &amp; Medical Centre               |
      | typeid               | 100                                            |
      | statusid             | 1                                              |
      | createdtime          | 2024-01-01 10:00:00                            |
      | modifiedtime         | 2024-01-01 10:00:00                            |

    When the data migration process is run for table 'services', ID '10045752' and method 'insert'
    And the data migration process is run for table 'services', ID '10055752' and method 'insert'
    Then there is 2 organisation, 2 location and 2 healthcare services created
    Then the organisation for service ID 10045752 has name St Peters Health Centre (Dr S'Souza)
    Then the organisation for service ID 10055752 has name The Surgery & Medical Centre
