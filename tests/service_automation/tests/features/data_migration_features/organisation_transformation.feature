@data-migration
Feature: Organisation Transformation

  Scenario: Organisation is created with correct ODS code mapping
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 4001001                           |
      | uid                                 | 400101                            |
      | name                                | GP: Organisation Mapping Test     |
      | odscode                             | E12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$10 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE1 1ST                           |
      | easting                             | 400001                            |
      | northing                            | 500001                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      | 01234567891                       |
      | fax                                 | 01234567892                       |
      | email                               | test@nhs.net                      |
      | web                                 | https://www.test.co.uk/           |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Organisation Mapping Test Surgery |
      | latitude                            | 51.5074                           |
      | longitude                           | -0.1278                           |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    When the service migration process is run for table 'services', ID '4001001' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And there is 1 organisation, 1 location and 1 healthcare services created
    And the organisation for service ID '4001001' has:
      | field                  | value          |
      | identifier_ODS_ODSCode | E12345         |
      | active                 | true           |
      | createdBy              | DATA_MIGRATION |

  Scenario: Organisation name is derived from service name for GP practices
    Given a "Service" exists in DoS with attributes
      | key                                 | value                               |
      | id                                  | 4001002                             |
      | uid                                 | 400102                              |
      | name                                | GP: Test Practice - Location Branch |
      | odscode                             | F12345                              |
      | openallhours                        | false                               |
      | publicreferralinstructions          |                                     |
      | telephonetriagereferralinstructions | Test referral instructions          |
      | restricttoreferrals                 | true                                |
      | address                             | Test Surgery$20 Test St$Test City   |
      | town                                | TEST CITY                           |
      | postcode                            | TE2 2ST                             |
      | easting                             | 400002                              |
      | northing                            | 500002                              |
      | publicphone                         | 01234567890                         |
      | nonpublicphone                      |                                     |
      | fax                                 | 01234567891                         |
      | email                               | test@nhs.net                        |
      | web                                 | https://www.test.co.uk/             |
      | createdby                           | HUMAN                               |
      | createdtime                         | 2020-01-01 10:00:00.000             |
      | modifiedby                          | ROBOT                               |
      | modifiedtime                        | 2024-01-01 10:00:00.000             |
      | lasttemplatename                    | Test Template                       |
      | lasttemplateid                      | 100001                              |
      | typeid                              | 100                                 |
      | parentid                            | 1001                                |
      | subregionid                         | 1001                                |
      | statusid                            | 1                                   |
      | organisationid                      |                                     |
      | returnifopenminutes                 |                                     |
      | publicname                          | Test Practice - Location Branch     |
      | latitude                            | 51.5074                             |
      | longitude                           | -0.1278                             |
      | professionalreferralinfo            |                                     |
      | lastverified                        |                                     |
      | nextverificationdue                 |                                     |
    When the service migration process is run for table 'services', ID '4001002' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And there is 1 organisation, 1 location and 1 healthcare services created
    And the organisation for service ID '4001002' has:
      | field | value         |
      | name  | Test Practice |

  Scenario: HealthcareService telecom is mapped correctly from DoS service fields
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 4001003                           |
      | uid                                 | 400103                            |
      | name                                | GP: Telecom Test Surgery          |
      | odscode                             | G12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$30 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE3 3ST                           |
      | easting                             | 400003                            |
      | northing                            | 500003                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      | 01234567891                       |
      | fax                                 | 01234567892                       |
      | email                               | telecom@nhs.net                   |
      | web                                 | https://www.telecom-test.co.uk/   |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Telecom Test Surgery              |
      | latitude                            | 51.5074                           |
      | longitude                           | -0.1278                           |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    When the service migration process is run for table 'services', ID '4001003' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And there is 1 organisation, 1 location and 1 healthcare services created
    And field 'telecom' on table 'healthcare-service' for id '7fa3406e-a2e4-5fb2-a427-6b49582eaa36' has content:
      """
      {
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": "01234567891",
          "email": "telecom@nhs.net",
          "web": "https://www.telecom-test.co.uk/"
        }
      }
      """

  Scenario: Organisation endpoints are created for service endpoints
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 4001004                           |
      | uid                                 | 400104                            |
      | name                                | GP: Endpoints Test Surgery        |
      | odscode                             | H12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$40 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE4 4ST                           |
      | easting                             | 400004                            |
      | northing                            | 500004                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      |                                   |
      | fax                                 | 01234567891                       |
      | email                               | endpoints@nhs.net                 |
      | web                                 | https://www.endpoints-test.co.uk/ |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Endpoints Test Surgery            |
      | latitude                            | 51.5074                           |
      | longitude                           | -0.1278                           |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    And a "ServiceEndpoint" exists in DoS with attributes
      | key                  | value                                                                             |
      | id                   | 4000001                                                                           |
      | endpointorder        | 1                                                                                 |
      | transport            | itk                                                                               |
      | format               | xml                                                                               |
      | interaction          | urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0 |
      | businessscenario     | Primary                                                                           |
      | address              | 1234567890ABCDEF                                                                  |
      | comment              | Test XML Endpoint                                                                 |
      | iscompressionenabled | uncompressed                                                                      |
      | serviceid            | 4001004                                                                           |
    When the service migration process is run for table 'services', ID '4001004' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And there is 1 organisation, 1 location and 1 healthcare services created
    And the organisation for service ID '4001004' has 1 endpoint with:
      | field          | value            |
      | connectionType | itk              |
      | address        | 1234567890ABCDEF |
      | order          | 1                |
