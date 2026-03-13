@data-migration
Feature: Data Migration - Pharmacy First

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @happy
  Scenario: Pharmacy First (M06) migration when parent Community Pharmacy has not been migrated yet
    # Parent Community Pharmacy (type 13) with ODS code FPQ49 exists in DoS but has NOT been migrated.
    # When the PF++ service (ODS FPQ49M06) is processed, the processor auto-migrates the parent first
    # (transaction 1), then creates the Pharmacy First HealthcareService linked to the parent
    # org/location (transaction 2).
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 167707                                                  |
      | uid                                 | 2000083534                                              |
      | name                                | Pharmacy: Craig Thomson Pharmacy, Brent, London         |
      | odscode                             | FPQ49                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 70-72 Walm Lane$Willesden Green$London                  |
      | town                                | LONDON                                                  |
      | postcode                            | NW2 4RA                                                 |
      | easting                             | 523387                                                  |
      | northing                            | 184769                                                  |
      | publicphone                         | 02084590833                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 | 00000 666666                                            |
      | email                               | 167707-fake@nhs.gov.uk                                  |
      | web                                 |                                                         |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2021-10-21 14:37:50.000                                 |
      | modifiedby                          | ROBOT                                                   |
      | modifiedtime                        | 2025-02-11 18:23:00.000                                 |
      | lasttemplatename                    | 202401 Tinashe Working Template                         |
      | lasttemplateid                      | 226211                                                  |
      | typeid                              | 13                                                      |
      | parentid                            | 167616                                                  |
      | subregionid                         | 21855                                                   |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Craig Thomson Pharmacy, Brent                           |
      | latitude                            | 51.5483336                                              |
      | longitude                           | -0.2218897                                              |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 137267                                                  |
      | uid                                 | 2000083535                                              |
      | name                                | PF++: London - Craig Thomson Pharmacy, Brent            |
      | odscode                             | FPQ49M06                                                |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 70-72 Walm Lane$Willesden Green$London                  |
      | town                                | LONDON                                                  |
      | postcode                            | NW2 4RA                                                 |
      | easting                             | 523387                                                  |
      | northing                            | 184769                                                  |
      | publicphone                         | 02084590833                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 137267-fake@nhs.gov.uk                                  |
      | web                                 |                                                         |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2021-10-21 14:37:50.000                                 |
      | modifiedby                          | ROBOT                                                   |
      | modifiedtime                        | 2025-02-11 18:23:00.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 167616                                                  |
      | subregionid                         | 21855                                                   |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Craig Thomson Pharmacy, Brent                           |
      | latitude                            | 51.5483336                                              |
      | longitude                           | -0.2218897                                              |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '137267' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#137267' with version 1

    # Validate that the Pharmacy First healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '137267' has content:
      """
      {
        "id": "d21082d3-df91-58c3-ba04-415ff3d7dfdd",
        "identifier_oldDoS_uid": "2000083535",
        "providedBy": "c979f90b-3651-502e-a0f8-37f100af0b44",
        "location": "67e57dd4-05e5-5d0b-ad48-ea31cdf70bc2",
        "name": "PF++: London - Craig Thomson Pharmacy, Brent",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """

  @happy
  Scenario: Pharmacy First (M06DSP) migration when parent Distance Selling Pharmacy has not been migrated yet
    # Parent Distance Selling Pharmacy (type 134) with ODS code FV499 exists in DoS but has NOT been migrated.
    # When the PF++ service (ODS FV499M06DSP) is processed, the processor auto-migrates the parent first
    # (transaction 1), then creates the Pharmacy First HealthcareService linked to the parent
    # org/location (transaction 2).
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214260                                                  |
      | uid                                 | 2000130084                                              |
      | name                                | Online Pharmacy - Dover                                 |
      | odscode                             | FV499                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 1 Castle Street$Dover$Kent                              |
      | town                                | DOVER                                                   |
      | postcode                            | CT16 1PJ                                                |
      | easting                             | 632000                                                  |
      | northing                            | 141000                                                  |
      | publicphone                         | 01304987654                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214260-fake@nhs.gov.uk                                  |
      | web                                 | www.onlinepharmacy.com                                  |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | Pharmacy Distance Selling Template                      |
      | lasttemplateid                      | 221812                                                  |
      | typeid                              | 134                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Online Pharmacy                                         |
      | latitude                            | 51.1270000                                              |
      | longitude                           | 1.3090000                                               |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214261                                                  |
      | uid                                 | 2000130085                                              |
      | name                                | PF++: Kent - Online Pharmacy - Dover                    |
      | odscode                             | FV499M06DSP                                             |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 1 Castle Street$Dover$Kent                              |
      | town                                | DOVER                                                   |
      | postcode                            | CT16 1PJ                                                |
      | easting                             | 632000                                                  |
      | northing                            | 141000                                                  |
      | publicphone                         | 01304987654                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214261-fake@nhs.gov.uk                                  |
      | web                                 | www.onlinepharmacy.com                                  |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Online Pharmacy                                         |
      | latitude                            | 51.1270000                                              |
      | longitude                           | 1.3090000                                               |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '214261' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214261' with version 1

    # Validate that the Pharmacy First healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '214261' has content:
      """
      {
        "id": "b88680b0-b7f9-527e-9a0d-a54e556b6b02",
        "identifier_oldDoS_uid": "2000130085",
        "providedBy": "d349e0bc-a8ef-50cd-972b-93ef215bd539",
        "location": "70229df2-984d-598c-877d-12c8ca999a92",
        "name": "PF++: Kent - Online Pharmacy - Dover",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """

  @happy
  Scenario: Pharmacy First (M06) migration when parent Community Pharmacy is already migrated
    # Parent Community Pharmacy (type 13) with ODS code FV500 is migrated first, establishing its
    # org/location in state. When the PF++ service (ODS FV500M06) is processed, the processor
    # reuses the existing parent org/location IDs directly from the state table — no second
    # parent migration occurs.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214262                                                  |
      | uid                                 | 2000130086                                              |
      | name                                | Boots - Ashford                                         |
      | odscode                             | FV500                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 5 Bank Street$Ashford$Kent                              |
      | town                                | ASHFORD                                                 |
      | postcode                            | TN23 1DA                                                |
      | easting                             | 601000                                                  |
      | northing                            | 142000                                                  |
      | publicphone                         | 01233111222                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214262-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | Pharmacy Template                                       |
      | lasttemplateid                      | 221808                                                  |
      | typeid                              | 13                                                      |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.1460000                                              |
      | longitude                           | 0.8740000                                               |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    # Migrate the parent pharmacy first so its state record and org/location exist in DynamoDB
    When the data migration process is run for table 'services', ID '214262' and method 'insert'

    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214263                                                  |
      | uid                                 | 2000130087                                              |
      | name                                | PF++: Kent - Boots - Ashford                            |
      | odscode                             | FV500M06                                                |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 5 Bank Street$Ashford$Kent                              |
      | town                                | ASHFORD                                                 |
      | postcode                            | TN23 1DA                                                |
      | easting                             | 601000                                                  |
      | northing                            | 142000                                                  |
      | publicphone                         | 01233111222                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214263-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.1460000                                              |
      | longitude                           | 0.8740000                                               |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '214263' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214263' with version 1

    # Validate the PF++ service is linked to the already-migrated parent org/location
    Then the 'healthcare-service' for service ID '214263' has content:
      """
      {
        "id": "40145796-932b-50b8-91c7-d1b3159499bc",
        "identifier_oldDoS_uid": "2000130087",
        "providedBy": "0ebb1699-c3af-5d86-b643-e200ca756361",
        "location": "3ad1f07f-82df-5eaf-bebf-2f06172ecab5",
        "name": "PF++: Kent - Boots - Ashford",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """
