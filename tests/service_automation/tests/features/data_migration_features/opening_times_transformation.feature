@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Opening times for service with service opening times
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10615752                                                    |
      | uid                                 | 138179                                                      |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire             |
      | odscode                             | M81094                                                      |
      | openallhours                        | FALSE                                                       |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
      | restricttoreferrals                 | TRUE                                                        |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                   |
      | town                                | EVESHAM                                                     |
      | postcode                            | WR11 4BS                                                    |
      | easting                             | 403453                                                      |
      | northing                            | 243634                                                      |
      | publicphone                         | 01386 761111                                                |
      | nonpublicphone                      | 99999 000000                                                |
      | fax                                 | 77777 000000                                                |
      | email                               |                                                             |
      | web                                 | www.abbeymedical.com                                        |
      | createdby                           | HUMAN                                                       |
      | createdtime                         | 2011-06-29 08:00:51.000                                     |
      | modifiedby                          | HUMAN                                                       |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                     |
      | lasttemplatename                    | Midlands template R46 Append PC                             |
      | lasttemplateid                      | 244764                                                      |
      | typeid                              | 100                                                         |
      | parentid                            | 150013                                                      |
      | subregionid                         | 150013                                                      |
      | statusid                            | 1                                                           |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Abbey Medical Practice                                      |
      | latitude                            | 52.0910543                                                  |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment |
      | id        | 3000000  |         |
      | serviceid | 10615752 |         |
      | dayid     | 1        | monday  |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001001  |
      | starttime           | 13:00:00 |
      | endtime             | 19:00:00 |
      | servicedayopeningid | 3000000  |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001000  |
      | starttime           | 08:00:00 |
      | endtime             | 12:00:00 |
      | servicedayopeningid | 3000000  |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment |
      | id        | 3000001  |         |
      | serviceid | 10615752 |         |
      | dayid     | 2        | tuesday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001002  |
      | starttime           | 08:00:00 |
      | endtime             | 19:00:00 |
      | servicedayopeningid | 3000001  |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment      |
      | id        | 3000002  |              |
      | serviceid | 10615752 |              |
      | dayid     | 8        | bank holiday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001003  |
      | starttime           | 09:00:00 |
      | endtime             | 15:00:00 |
      | servicedayopeningid | 3000002  |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment  |
      | id        | 3000003  |          |
      | serviceid | 10615752 |          |
      | dayid     | 6        | saturday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    | comment  |
      | id                  | 3001004  |          |
      | starttime           | 00:00:00 |          |
      | endtime             | 23:59:00 | all day? |
      | servicedayopeningid | 3000003  |          |

    When the data migration process is run for table 'services', ID '10615752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'openingTime' on table 'healthcare-service' for id 'e494ad1a-d8b5-5734-b46a-85cba1a28c24' has content:
      """
      {
          "openingTime": [
              {
                  "allDay": false,
                  "startTime": "08:00:00",
                  "dayOfWeek": "mon",
                  "endTime": "12:00:00",
                  "category": "availableTime"
              },
              {
                  "allDay": false,
                  "startTime": "13:00:00",
                  "dayOfWeek": "mon",
                  "endTime": "19:00:00",
                  "category": "availableTime"
              },
              {
                  "allDay": false,
                  "startTime": "08:00:00",
                  "dayOfWeek": "tue",
                  "endTime": "19:00:00",
                  "category": "availableTime"
              },
              {
                  "category": "availableTimePublicHolidays",
                  "startTime": "09:00:00",
                  "endTime": "15:00:00"
              },
              {
                  "allDay": false,
                  "startTime": "00:00:00",
                  "dayOfWeek": "sat",
                  "endTime": "23:59:00",
                  "category": "availableTime"
              }
          ]
      }
      """

  Scenario: Opening times for service with variations over service days
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10625752                                                    |
      | uid                                 | 138179                                                      |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire             |
      | odscode                             | M81094                                                      |
      | openallhours                        | FALSE                                                       |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
      | restricttoreferrals                 | TRUE                                                        |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                   |
      | town                                | EVESHAM                                                     |
      | postcode                            | WR11 4BS                                                    |
      | easting                             | 403453                                                      |
      | northing                            | 243634                                                      |
      | publicphone                         | 01386 761111                                                |
      | nonpublicphone                      | 99999 000000                                                |
      | fax                                 | 77777 000000                                                |
      | email                               |                                                             |
      | web                                 | www.abbeymedical.com                                        |
      | createdby                           | HUMAN                                                       |
      | createdtime                         | 2011-06-29 08:00:51.000                                     |
      | modifiedby                          | HUMAN                                                       |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                     |
      | lasttemplatename                    | Midlands template R46 Append PC                             |
      | lasttemplateid                      | 244764                                                      |
      | typeid                              | 100                                                         |
      | parentid                            | 150013                                                      |
      | subregionid                         | 150013                                                      |
      | statusid                            | 1                                                           |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Abbey Medical Practice                                      |
      | latitude                            | 52.0910543                                                  |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |


    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment |
      | id        | 3000010  |         |
      | serviceid | 10625752 |         |
      | dayid     | 1        | monday  |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001010  |
      | starttime           | 08:00:00 |
      | endtime             | 12:00:00 |
      | servicedayopeningid | 3000010  |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001011  |
      | starttime           | 13:00:00 |
      | endtime             | 19:00:00 |
      | servicedayopeningid | 3000010  |


    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment |
      | id        | 3000011  |         |
      | serviceid | 10625752 |         |
      | dayid     | 2        | tuesday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001012  |
      | starttime           | 08:00:00 |
      | endtime             | 19:00:00 |
      | servicedayopeningid | 3000011  |


    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment      |
      | id        | 3000012  |              |
      | serviceid | 10625752 |              |
      | dayid     | 8        | bank holiday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    |
      | id                  | 3001013  |
      | starttime           | 09:00:00 |
      | endtime             | 15:00:00 |
      | servicedayopeningid | 3000012  |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment  |
      | id        | 3000013  |          |
      | serviceid | 10625752 |          |
      | dayid     | 6        | saturday |
    And a "ServiceDayOpeningTime" exists in DoS with attributes
      | key                 | value    | comment  |
      | id                  | 3001014  |          |
      | starttime           | 00:00:00 |          |
      | endtime             | 23:59:00 | all day? |
      | servicedayopeningid | 3000013  |          |


    And a "ServiceSpecifiedOpeningDate" exists in DoS with attributes
      | key       | value      | comment        |
      | id        | 9000000    |                |
      | date      | 2025-12-02 | also a tuesday |
      | serviceid | 10625752   |                |
    And a "ServiceSpecifiedOpeningTime" exists in DoS with attributes
      | key                          | value      |
      | id                           | 8000000    |
      | starttime                    | 10:00:00   |
      | endtime                      | 15:00:00   |
      | isclosed                     | false      |
      | servicespecifiedopeningdateid| 9000000    |


    And a "ServiceSpecifiedOpeningDate" exists in DoS with attributes
      | key       | value      | comment   |
      | id        | 9000001    |           |
      | date      | 2025-12-03 |           |
      | serviceid | 10625752   | wednesday |
    And a "ServiceSpecifiedOpeningTime" exists in DoS with attributes
      | key                          | value      |
      | id                           | 8000001    |
      | starttime                    | 06:00:00   |
      | endtime                      | 18:00:00   |
      | isclosed                     | false      |
      | servicespecifiedopeningdateid| 9000001    |

    And a "ServiceSpecifiedOpeningDate" exists in DoS with attributes
      | key       | value      | comment               |
      | id        | 9000002    |                       |
      | date      | 2025-12-26 |                       |
      | serviceid | 10625752   | specific bank holiday |
    And a "ServiceSpecifiedOpeningTime" exists in DoS with attributes
      | key                          | value      |
      | id                           | 8000002    |
      | starttime                    | 00:00:00   |
      | endtime                      | 00:00:00   |
      | isclosed                     | true       |
      | servicespecifiedopeningdateid| 9000002    |


    When the data migration process is run for table 'services', ID '10625752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'openingTime' on table 'healthcare-service' for id 'fd7d4681-abde-5de6-8742-375a4e2eea00' has content:
      """
      {
          "openingTime": [
              {
                  "allDay": false,
                  "startTime": "08:00:00",
                  "dayOfWeek": "mon",
                  "endTime": "12:00:00",
                  "category": "availableTime"
              },
              {
                  "allDay": false,
                  "startTime": "13:00:00",
                  "dayOfWeek": "mon",
                  "endTime": "19:00:00",
                  "category": "availableTime"
              },
              {
                  "allDay": false,
                  "startTime": "08:00:00",
                  "dayOfWeek": "tue",
                  "endTime": "19:00:00",
                  "category": "availableTime"
              },
              {
                  "category": "availableTimePublicHolidays",
                  "startTime": "09:00:00",
                  "endTime": "15:00:00"
              },
              {
                  "allDay": false,
                  "startTime": "00:00:00",
                  "dayOfWeek": "sat",
                  "endTime": "23:59:00",
                  "category": "availableTime"
              },
              {
                  "description": null,
                  "startTime": "2025-12-02T10:00:00",
                  "endTime": "2025-12-02T15:00:00",
                  "category": "availableTimeVariations"
              },
              {
                  "description": null,
                  "startTime": "2025-12-03T06:00:00",
                  "endTime": "2025-12-03T18:00:00",
                  "category": "availableTimeVariations"
              },
              {
                  "description": null,
                  "startTime": "2025-12-26T00:00:00",
                  "endTime": "2025-12-26T00:00:00",
                  "category": "notAvailable"
              }
          ]
      }
      """

  Scenario: Opening times for service with no opening times on a service day result in day being skipped
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10695752                                                    |
      | uid                                 | 138179                                                      |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire             |
      | odscode                             | M81094                                                      |
      | openallhours                        | FALSE                                                       |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752 |
      | restricttoreferrals                 | TRUE                                                        |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                   |
      | town                                | EVESHAM                                                     |
      | postcode                            | WR11 4BS                                                    |
      | easting                             | 403453                                                      |
      | northing                            | 243634                                                      |
      | publicphone                         | 01386 761111                                                |
      | nonpublicphone                      | 99999 000000                                                |
      | fax                                 | 77777 000000                                                |
      | email                               |                                                             |
      | web                                 | www.abbeymedical.com                                        |
      | createdby                           | HUMAN                                                       |
      | createdtime                         | 2011-06-29 08:00:51.000                                     |
      | modifiedby                          | HUMAN                                                       |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                     |
      | lasttemplatename                    | Midlands template R46 Append PC                             |
      | lasttemplateid                      | 244764                                                      |
      | typeid                              | 100                                                         |
      | parentid                            | 150013                                                      |
      | subregionid                         | 150013                                                      |
      | statusid                            | 1                                                           |
      | organisationid                      |                                                             |
      | returnifopenminutes                 |                                                             |
      | publicname                          | Abbey Medical Practice                                      |
      | latitude                            | 52.0910543                                                  |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |

    And a "ServiceDayOpening" exists in DoS with attributes
      | key       | value    | comment |
      | id        | 3000100  |         |
      | serviceid | 10695752 |         |
      | dayid     |    1      |        |
    When the data migration process is run for table 'services', ID '10695752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'openingTime' on table 'healthcare-service' for id '8bfe926e-f3fb-5d4a-800a-d8bb96c67bd9' has content:
      """
      {
          "openingTime": []
      }
      """
