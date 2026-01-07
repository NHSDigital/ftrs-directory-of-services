@data-migration
Feature: Data Migration State Tests
  Scenario: State stored correctly after initial migration of a service
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

    When the service migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the validated source record has the following changes before migration for service ID '10005752':
      | change                                                                                                     |
      | Value of root['publicphone'] changed from "01386 761111" to "01386761111".                                 |
      | Type of root['nonpublicphone'] changed from str to NoneType and value changed from "99999 000000" to None. |
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
    Then the migration state of service ID '10005752' is version 1
    And the migration state of service ID '10005752' contains a 'organisation' with ID '92c51dc4-9b80-54c1-bfcf-62826d6823f0'
    And the migration state of service ID '10005752' contains a 'location' with ID 'fbb2340b-53e0-56f9-ada3-ef5728ca8f98'
    And the migration state of service ID '10005752' contains a 'healthcare_service' with ID '48865e3d-b8f0-508b-8520-29b3113da1e3'
    And the migration state of service ID '10005752' matches the stored records
    And the migration state of service ID '10005752' contains 2 validation issues
    And the migration state of service ID '10005752' has the following validation issues:
      | expression     | severity | code             | diagnostics             | value       |
      | email          | error    | email_not_string | Email must be a string  | None        |
      | nonpublicphone | error    | invalid_format   | Phone number is invalid | 99999000000 |

  Scenario: Organisation change detected
    # Perform initial migration
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

    When the service migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the validated source record has the following changes before migration for service ID '10005752':
      | change                                                                                                     |
      | Value of root['publicphone'] changed from "01386 761111" to "01386761111".                                 |
      | Type of root['nonpublicphone'] changed from str to NoneType and value changed from "99999 000000" to None. |

    Then the migration state of service ID '10005752' is version 1
    And the migration state of service ID '10005752' matches the stored records
    And the migration state of service ID '10005752' contains 2 validation issues
    And the migration state of service ID '10005752' has the following validation issues:
      | expression     | severity | code             | diagnostics             | value       |
      | email          | error    | email_not_string | Email must be a string  | None        |
      | nonpublicphone | error    | invalid_format   | Phone number is invalid | 99999000000 |

    # Update the publicname to simulate an organisation change
    Given the mock logger is reset
    Given the "Service" with id "10005752" is updated with attributes
      | key        | value                          |
      | publicname | Abbey Medical Practice Updated |

    When the service migration process is run for table 'services', ID '10005752' and method 'update'
    Then the service migration process completes successfully
    Then there is 1 organisation, 1 location and 1 healthcare services created


    # TODO: Uncomment on completion of FTRS-1371
    # Then the migration state of service ID '10005752' is version 2
    # And the migration state of service ID '10005752' matches the stored records

    Then there is an Organisation update with changes:
      | change                                                                                           |
      | Value of root['name'] changed from "Abbey Medical Practice" to "Abbey Medical Practice Updated". |
    Then there is no Location update
    Then there is no Healthcare Service update

  Scenario: Location change detected
    # Perform initial migration
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

    When the service migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the validated source record has the following changes before migration for service ID '10005752':
      | change                                                                                                     |
      | Value of root['publicphone'] changed from "01386 761111" to "01386761111".                                 |
      | Type of root['nonpublicphone'] changed from str to NoneType and value changed from "99999 000000" to None. |

    Then the migration state of service ID '10005752' is version 1
    And the migration state of service ID '10005752' matches the stored records
    And the migration state of service ID '10005752' contains 2 validation issues
    And the migration state of service ID '10005752' has the following validation issues:
      | expression     | severity | code             | diagnostics             | value       |
      | email          | error    | email_not_string | Email must be a string  | None        |
      | nonpublicphone | error    | invalid_format   | Phone number is invalid | 99999000000 |

    # Update the publicname to simulate an organisation change
    Given the mock logger is reset
    Given the "Service" with id "10005752" is updated with attributes
      | key       | value   |
      | latitude  | 52.0000 |
      | longitude | -1.9000 |

    When the service migration process is run for table 'services', ID '10005752' and method 'update'
    Then the service migration process completes successfully
    Then there is 1 organisation, 1 location and 1 healthcare services created

    # TODO: Uncomment on completion of FTRS-1371
    # Then the migration state of service ID '10005752' is version 2
    # And the migration state of service ID '10005752' matches the stored records

    Then there is no Organisation update
    Then there is a Location update with changes:
      | change                                                                                 |
      | Value of root['positionGCS']['latitude'] changed from 52.0910543000 to 52.0000000000.  |
      | Value of root['positionGCS']['longitude'] changed from -1.9510030000 to -1.9000000000. |
    Then there is no Healthcare Service update

  Scenario: Healthcare service change detected
    # Perform initial migration
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

    When the service migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the validated source record has the following changes before migration for service ID '10005752':
      | change                                                                                                     |
      | Value of root['publicphone'] changed from "01386 761111" to "01386761111".                                 |
      | Type of root['nonpublicphone'] changed from str to NoneType and value changed from "99999 000000" to None. |

    Then the migration state of service ID '10005752' is version 1
    And the migration state of service ID '10005752' matches the stored records
    And the migration state of service ID '10005752' contains 2 validation issues
    And the migration state of service ID '10005752' has the following validation issues:
      | expression     | severity | code             | diagnostics             | value       |
      | email          | error    | email_not_string | Email must be a string  | None        |
      | nonpublicphone | error    | invalid_format   | Phone number is invalid | 99999000000 |

    # Update the publicname to simulate an organisation change
    Given the mock logger is reset
    Given the "Service" with id "10005752" is updated with attributes
      | key         | value       |
      | publicphone | 01234567890 |

    When the service migration process is run for table 'services', ID '10005752' and method 'update'
    Then the service migration process completes successfully
    Then there is 1 organisation, 1 location and 1 healthcare services created

    # TODO: Uncomment on completion of FTRS-1371
    # Then the migration state of service ID '10005752' is version 2
    # And the migration state of service ID '10005752' matches the stored records

    Then there is no Organisation update
    Then there is no Location update
    Then there is a Healthcare Service update with changes:
      | change                                                                                |
      | Value of root['telecom']['phone_public'] changed from "01386761111" to "01234567890". |
