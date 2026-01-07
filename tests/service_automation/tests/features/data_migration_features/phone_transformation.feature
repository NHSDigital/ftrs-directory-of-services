@data-migration
Feature: Phone Transformation

  # Background:
  #     Given the test environment is configured
  #     And the DoS database has test data
  #     And DynamoDB tables are ready

  Scenario Outline: Valid phone number formats are transformed correctly
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                              |
      | id                                  | <service_id>                                       |
      | uid                                 | <uid>                                              |
      | name                                | GP: <format_name> Phone Surgery                    |
      | odscode                             | <ods_code>                                         |
      | isnational                          |                                                    |
      | openallhours                        | false                                              |
      | publicreferralinstructions          |                                                    |
      | telephonetriagereferralinstructions | Valid phone referral instructions                  |
      | restricttoreferrals                 | true                                               |
      | address                             | Valid Surgery$10 Test Street$Test City$Test County |
      | town                                | TEST CITY                                          |
      | postcode                            | TE1 1ST                                            |
      | easting                             | 400000                                             |
      | northing                            | 500000                                             |
      | publicphone                         | <public_phone>                                     |
      | nonpublicphone                      | <private_phone>                                    |
      | fax                                 | 01234567892                                        |
      | email                               | valid.phone@nhs.net                                |
      | web                                 | https://www.validphonesurgery.co.uk/               |
      | createdby                           | HUMAN                                              |
      | createdtime                         | 2020-01-01 10:00:00.000                            |
      | modifiedby                          | ROBOT                                              |
      | modifiedtime                        | 2024-01-01 10:00:00.000                            |
      | lasttemplatename                    | Test Template                                      |
      | lasttemplateid                      | 100001                                             |
      | typeid                              | 100                                                |
      | parentid                            | 1527                                               |
      | subregionid                         | 1527                                               |
      | statusid                            | 1                                                  |
      | organisationid                      |                                                    |
      | returnifopenminutes                 |                                                    |
      | publicname                          | <format_name> Phone Surgery                        |
      | latitude                            | 51.5074                                            |
      | longitude                           | -0.1278                                            |
      | professionalreferralinfo            |                                                    |
      | lastverified                        |                                                    |
      | nextverificationdue                 |                                                    |

    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    # Then field 'migrationNotes' on table 'healthcare-service' for id '<healthcare_service_id>' has content:
    #   """
    #   {
    #     "migrationNotes": []
    #   }
    #   """
    Then field 'telecom' on table 'healthcare-service' for id '<healthcare_service_id>' has content:
      """
      {
        "telecom": {
          "email": "valid.phone@nhs.net",
          "phone_private": "<expected_private>",
          "phone_public": "<expected_public>",
          "web": "https://www.validphonesurgery.co.uk/"
        }
      }
      """

    Examples:
      | service_id | uid    | ods_code | format_name       | public_phone    | private_phone   | expected_public | expected_private | healthcare_service_id                |
      | 2001001    | 200101 | A10001   | No Spaces         | 01234567890     | 01234567891     | 01234567890     | 01234567891      | 0705993b-ffc5-54f9-9f3d-b1dad562233d |
      | 2001002    | 200102 | A10002   | Five-Six Format   | 01234 567890    | 02345 678901    | 01234567890     | 02345678901      | 7e8c0a33-07a4-5adb-84ff-c82686ec0766 |
      | 2001003    | 200103 | A10003   | Four-Three-Four   | 0123 456 7890   | 0234 567 8901   | 01234567890     | 02345678901      | 5ed82a7f-f379-5571-9726-56f399afaba0 |
      | 2001004    | 200104 | A10004   | Five-Three-Three  | 01234 567 890   | 02345 678 901   | 01234567890     | 02345678901      | b69933b5-3a97-546d-a1e3-d29662e8c2df |
      | 2001005    | 200105 | A10005   | Three-Four-Four   | 012 3456 7890   | 023 4567 8901   | 01234567890     | 02345678901      | d2833d02-b93b-508b-99d5-ea41de69f212 |
      | 2001006    | 200106 | A10006   | With Country Code | +44 1234 567890 | +44 2345 678901 | 01234567890     | 02345678901      | 6c92db19-0fe9-5750-9fd8-d37158a41b32 |


  Scenario Outline: Invalid phone number formats trigger migration notes
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                |
      | id                                  | <service_id>                                         |
      | uid                                 | <uid>                                                |
      | name                                | GP: <error_type> Phone Surgery                       |
      | odscode                             | <ods_code>                                           |
      | isnational                          |                                                      |
      | openallhours                        | false                                                |
      | publicreferralinstructions          |                                                      |
      | telephonetriagereferralinstructions | Invalid phone referral instructions                  |
      | restricttoreferrals                 | true                                                 |
      | address                             | Invalid Surgery$20 Test Street$Test City$Test County |
      | town                                | TEST CITY                                            |
      | postcode                            | TE2 2ST                                              |
      | easting                             | 400001                                               |
      | northing                            | 500001                                               |
      | publicphone                         | <public_phone>                                       |
      | nonpublicphone                      | <private_phone>                                      |
      | fax                                 | 01234567894                                          |
      | email                               | invalid.phone@nhs.net                                |
      | web                                 | https://www.invalidphone.co.uk/                      |
      | createdby                           | HUMAN                                                |
      | createdtime                         | 2020-02-01 10:00:00.000                              |
      | modifiedby                          | ROBOT                                                |
      | modifiedtime                        | 2024-02-01 10:00:00.000                              |
      | lasttemplatename                    | Test Template 2                                      |
      | lasttemplateid                      | 100002                                               |
      | typeid                              | 100                                                  |
      | parentid                            | 1527                                                 |
      | subregionid                         | 1527                                                 |
      | statusid                            | 1                                                    |
      | organisationid                      |                                                      |
      | returnifopenminutes                 |                                                      |
      | publicname                          | <error_type> Phone Surgery                           |
      | latitude                            | 51.5075                                              |
      | longitude                           | -0.1279                                              |
      | professionalreferralinfo            |                                                      |
      | lastverified                        |                                                      |
      | nextverificationdue                 |                                                      |

    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the service migration process completes successfully
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    # Then field 'migrationNotes' on table 'healthcare-service' for id '<healthcare_service_id>' has content:
    #   """
    #   {
    #     "migrationNotes": [
    #       <migration_notes>
    #     ]
    #   }
    #   """
    Then field 'telecom' on table 'healthcare-service' for id '<healthcare_service_id>' has content:
      """
      {
        "telecom": {
          "email": "invalid.phone@nhs.net",
          "phone_private": <expected_private>,
          "phone_public": <expected_public>,
          "web": "https://www.invalidphone.co.uk/"
        }
      }
      """

    Examples:
      | service_id | uid    | ods_code | error_type      | public_phone              | private_phone | expected_public | expected_private | migration_notes                                                                                                                                                                 | healthcare_service_id                |
      | 2002001    | 200201 | B10001   | Invalid Format  | INVALID123                | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_format,message:Phone number is invalid,value:INVALID123"                                                                                 | 1e6ed268-b391-5b8b-9046-ea47c1569097 |
      | 2002002    | 200202 | B10002   | Text Instead    | NOTANUMBER                | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_format,message:Phone number is invalid,value:NOTANUMBER"                                                                                 | c2744618-da70-5711-8bed-ac13ee6a68a3 |
      | 2002003    | 200203 | B10003   | Empty String    |                           |               | null            | null             | "field:['publicphone'] ,error: empty,message:Phone number cannot be empty,value:None", "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None" | fc4a7bc5-163e-528f-8dbc-23984753ffaf |
      | 2002004    | 200204 | B10004   | Text NA         | na                        | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:na"                                                                                  | 67505261-ba65-5293-8709-505d9e7d2f80 |
      | 2002005    | 200205 | B10005   | Too Short       | 123                       | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:123"                                                                                 | 3e34f22c-7d7a-5623-85b0-e75b67cdd30b |
      | 2002006    | 200206 | B10006   | Too Long        | 01234567890123            | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:01234567890123"                                                                      | f09681e5-e8c1-53f6-9682-b496f918f3f3 |
      | 2002007    | 200207 | B10007   | Multiple Phones | 01234567890 / 09876543210 | 01234567893   | null            | "01234567893"    | "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:01234567890/09876543210"                                                             | 5956c4df-be70-55b0-8115-8ffa1405c32b |
