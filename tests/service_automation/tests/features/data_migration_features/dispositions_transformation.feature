@data-migration
Feature: Data Migration
  Scenario: Disposition codes for a service are migrated
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10175752                                                    |
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

    And a "ServiceDisposition" exists in DoS with attributes
      | key           | value    | comment                                                     |
      | id            | 7000000  |                                                             |
      | serviceid     | 10175752 |                                                             |
      | dispositionid | 4        | To contact a Primary Care Service within 2 hours, DX05, 120 |
    And a "ServiceDisposition" exists in DoS with attributes
      | key           | value    | comment                                                     |
      | id            | 7000001  |                                                             |
      | serviceid     | 10175752 |                                                             |
      | dispositionid | 5        | To contact a Primary Care Service within 6 hours, DX06, 360 |

    When the service migration process is run for table 'services', ID '10175752' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'dispositions' on table 'healthcare-service' for id 'a50c907c-56d8-541b-946f-58f5e0b2f090' has content:
      """
      {
        "dispositions": [
          "DX05",
          "DX06"
        ]
      }
      """

  Scenario: Disposition codes with a empty DX code is populated with empty list and  migrated
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10275752                                                    |
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
    And a "Disposition" exists in DoS with attributes
      | key             | value                                  | comment                 |
      | id              | 1000                                   |                         |
      | name            | Test disposition, null time and dxcode |                         |
      | dxcode          |                                        | nullable, leaving empty |
      | dispositiontime |                                        | nullable, leaving empty |
    And a "ServiceDisposition" exists in DoS with attributes
      | key           | value    | comment |
      | id            | 7000000  |         |
      | serviceid     | 10275752 |         |
      | dispositionid | 1000     |         |
    When the service migration process is run for table 'services', ID '10275752' and method 'insert'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'dispositions' on table 'healthcare-service' for id '70bfeb90-7d79-5d1f-bbf0-0b1faaf6ffe2' has content:
      """
      {
        "dispositions": []
      }
      """
