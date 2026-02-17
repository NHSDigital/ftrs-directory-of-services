@component
Feature: HealthcareService - Create HealthcareService

  As a user of the CRUD API
  I want to be able to create a new healthcare service
  So that I can manage my healthcare services in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Create a new healthcare service with valid data
    When I call the CRUD API "POST /HealthcareService" endpoint with the following JSON body:
      """
      {
        "active": true,
        "category": "GP Services",
        "type": "GP Consultation Service",
        "providedBy": "00000000-0000-0000-0000-11111111111a",
        "location": "00000000-0000-0000-0000-11111111111b",
        "name": "Test Healthcare Service",
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": null,
          "email": "test@nhs.net",
          "web": "https://www.nhs.uk"
        },
        "openingTime": null,
        "symptomGroupSymptomDiscriminators": [],
        "dispositions": [],
        "ageEligibilityCriteria": null
      }
      """
    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "healthcare_service_id"
    And the "createdTime" value is extracted from the response body as "created_time"
    And the "lastUpdated" value is extracted from the response body as "last_updated_time"

    And the response body should match the following JSON:
      """
      {
        "id": "{{healthcare_service_id}}",
        "createdTime": "{{created_time}}",
        "createdBy": {
          "type": "app",
          "value": "SYSTEM",
          "display": "SYSTEM"
        },
        "lastUpdated": "{{last_updated_time}}",
        "lastUpdatedBy": {
          "type": "app",
          "value": "SYSTEM",
          "display": "SYSTEM"
        },
        "identifier_oldDoS_uid": null,
        "active": true,
        "category": "GP Services",
        "type": "GP Consultation Service",
        "providedBy": "00000000-0000-0000-0000-11111111111a",
        "location": "00000000-0000-0000-0000-11111111111b",
        "name": "Test Healthcare Service",
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": null,
          "email": "test@nhs.net",
          "web": "https://www.nhs.uk"
        },
        "openingTime": null,
        "symptomGroupSymptomDiscriminators": [],
        "dispositions": [],
        "ageEligibilityCriteria": null
      }
      """

  Scenario: Create a healthcare service with missing required fields
    When I call the CRUD API "POST /HealthcareService" endpoint with the following JSON body:
      """
      {
        "category": "GP Services",
        "active": true,
        "providedBy": "00000000-0000-0000-0000-11111111111a",
        "location": "00000000-0000-0000-0000-11111111111b",
        "name": "Test Healthcare Service",
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": null,
          "email": null,
          "web": null
        },
        "openingTime": null,
        "symptomGroupSymptomDiscriminators": [],
        "dispositions": [],
        "ageEligibilityCriteria": null
      }
      """

    Then the response status code should be 422
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "invalid",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_PARAM_INVALID",
                  "display": "Parameter content is invalid"
                }
              ],
              "text": "1 validation error:\n  {'type': 'missing', 'loc': ('body', 'type'), 'msg': 'Field required', 'input': {'category': 'GP Services', 'active': True, 'providedBy': '00000000-0000-0000-0000-11111111111a', 'location': '00000000-0000-0000-0000-11111111111b', 'name': 'Test Healthcare Service', 'telecom': {'phone_public': '01234567890', 'phone_private': None, 'email': None, 'web': None}, 'openingTime': None, 'symptomGroupSymptomDiscriminators': [], 'dispositions': [], 'ageEligibilityCriteria': None}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/healthcare.py\", line 138, in post_healthcare_service\n    POST /HealthcareService/"
            },
            "diagnostics": "1 validation error:\n  {'type': 'missing', 'loc': ('body', 'type'), 'msg': 'Field required', 'input': {'category': 'GP Services', 'active': True, 'providedBy': '00000000-0000-0000-0000-11111111111a', 'location': '00000000-0000-0000-0000-11111111111b', 'name': 'Test Healthcare Service', 'telecom': {'phone_public': '01234567890', 'phone_private': None, 'email': None, 'web': None}, 'openingTime': None, 'symptomGroupSymptomDiscriminators': [], 'dispositions': [], 'ageEligibilityCriteria': None}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/healthcare.py\", line 138, in post_healthcare_service\n    POST /HealthcareService/"
          }
        ]
      }
      """
