@component
Feature: HealthcareService - Delete HealthcareService

  As a user of the CRUD API
  I want to be able to delete a healthcare service
  So that I can manage my healthcare services in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Delete a valid healthcare service
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

    When I call the CRUD API "GET /HealthcareService/{{healthcare_service_id}}" endpoint
    Then the response status code should be 200

    When I call the CRUD API "DELETE /HealthcareService/{{healthcare_service_id}}" endpoint
    Then the response status code should be 204

    When I call the CRUD API "GET /HealthcareService/{{healthcare_service_id}}" endpoint
    Then the response status code should be 404

  Scenario: Delete a healthcare service with a non-existent ID
    When I call the CRUD API "DELETE /HealthcareService/00000000-0000-0000-0000-00000000000a" endpoint
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "Healthcare Service not found"
      }
      """

  Scenario: Delete a healthcare service with an invalid ID format
    When I call the CRUD API "DELETE /HealthcareService/invalid-uuid-format" endpoint
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
              "text": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'service_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/healthcare.py\", line 107, in delete_healthcare_service\n    DELETE /HealthcareService/{service_id}"
            },
            "diagnostics": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'service_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/healthcare.py\", line 107, in delete_healthcare_service\n    DELETE /HealthcareService/{service_id}"
          }
        ]
      }
      """
