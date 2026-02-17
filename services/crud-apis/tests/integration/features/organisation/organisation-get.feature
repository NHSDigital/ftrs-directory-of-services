@component
Feature: Organisations - Get Organisation

  As a user of the CRUD API
  I want to be able to retrieve an organisation by its ID
  So that I can view the details of an organisation in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Get an organisation by ID
    When I call the CRUD API "POST /Organization" endpoint with the following JSON body:
      """
      {
        "identifier_ODS_ODSCode": "ABC123",
        "name": "Test Organisation",
        "active": true,
        "type": "GP Practice",
        "telecom": []
      }
      """
    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "organisation_id"
    And the "createdTime" value is extracted from the response body as "created_time"
    And the "lastUpdated" value is extracted from the response body as "last_updated_time"

    When I call the CRUD API "GET /Organization/{{organisation_id}}" endpoint
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      {
        "id": "{{organisation_id}}",
        "createdTime": "{{created_time}}",
        "createdBy": {
          "type": "app",
          "value": "crud-integration-tests",
          "display": "CRUD API"
        },
        "lastUpdated": "{{last_updated_time}}",
        "lastUpdatedBy": {
          "type": "app",
          "value": "crud-integration-tests",
          "display": "CRUD API"
        },
        "identifier_oldDoS_uid": null,
        "identifier_ODS_ODSCode": "ABC123",
        "active": true,
        "name": "Test Organisation",
        "type": "GP Practice",
        "primary_role_code": null,
        "non_primary_role_codes": [],
        "telecom": [],
        "endpoints": [],
        "legalDates": null
      }
      """

  Scenario: Get an organisation with invalid ID format
    When I call the CRUD API "GET /Organization/invalid-uuid-format" endpoint
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
              "text": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'organisation_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/organisation.py\", line 93, in get_organisation_by_id\n    GET /Organization/{organisation_id}"
            },
            "diagnostics": "1 validation error:\n  {'type': 'uuid_parsing', 'loc': ('path', 'organisation_id'), 'msg': 'Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1', 'input': 'invalid-uuid-format', 'ctx': {'error': 'invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1'}}\n\n  File \"/Users/thomas/repos/github.com/NHSDigital/ftrs-directory-of-services/services/crud-apis/dos_ingest/router/organisation.py\", line 93, in get_organisation_by_id\n    GET /Organization/{organisation_id}"
          }
        ]
      }
      """

  Scenario: Organisation not found
    When I call the CRUD API "GET /Organization/00000000-0000-0000-0000-00000000000a" endpoint
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "Organisation not found"
      }
      """
