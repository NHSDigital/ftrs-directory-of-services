@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Latitude and longitude is migrated
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10105752                                                    |
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
    When the data migration process is run for table 'services', ID '10105752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'positionGCS' on table 'location' for id 'a9fc6829-23bd-5bbe-83cb-32be4a50eaa2' has content:
      """
      {
        "positionGCS": {
          "latitude": "52.0910543000",
          "longitude": "-1.9510030000"
        }
      }
      """


  Scenario: Longitude is not copied over when latitude is missing
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10105752                                                    |
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
      | latitude                            |                                                             |
      | longitude                           | -1.951003                                                   |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |
    When the data migration process is run for table 'services', ID '10105752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'positionGCS' on table 'location' for id 'a9fc6829-23bd-5bbe-83cb-32be4a50eaa2' has content:
      """
      {
        "positionGCS": null
      }
      """


  Scenario: Latitude is not copied over when longitude is missing
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                       |
      | id                                  | 10105753                                                    |
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
      | longitude                           |                                                             |
      | professionalreferralinfo            | Nope                                                        |
      | lastverified                        |                                                             |
      | nextverificationdue                 |                                                             |
    When the data migration process is run for table 'services', ID '10105753' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then field 'positionGCS' on table 'location' for id '9042741e-5d30-5b5c-ac22-475215b3f96a' has content:
      """
      {
        "positionGCS": null
      }
      """
