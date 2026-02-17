@component
Feature: Organisations - Update Organisation

  As a user of the CRUD API
  I want to be able to update an existing organisation
  So that I can keep the details of my organisations up to date in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Update an organisation name
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

    When I call the CRUD API "PUT /Organization/{{organisation_id}}" endpoint with the following JSON body:
      """
      {
        "id": "{{organisation_id}}",
        "resourceType": "Organization",
        "identifier": [
          {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "ABC123"
          }
        ],
        "name": "Updated Test Organisation",
        "active": false,
        "telecom": []
      }
      """
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "information",
            "code": "success",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_UPDATED",
                  "display": "Existing resource updated"
                }
              ],
              "text": "Organisation updated successfully"
            },
            "diagnostics": "Organisation updated successfully"
          }
        ]
      }
      """

    When I call the CRUD API "GET /Organization/{{organisation_id}}" endpoint
    Then the response status code should be 200
    And the "name" field in the response body should be "Updated Test Organisation"
    And the response body should contain the following JSON:
      """
      {
        "lastUpdatedBy": {
          "display": "ODS",
          "type": "app",
          "value": "crud-integration-tests"
        }
      }
      """

  Scenario: Update an organisation with a duplicate ODS code
    When I call the CRUD API "POST /Organization" endpoint with the following JSON body:
      """
      {
        "identifier_ODS_ODSCode": "DUPLICATE123",
        "name": "First Organisation",
        "active": true,
        "type": "GP Practice",
        "telecom": []
      }
      """

    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "first_organisation_id"

    When I call the CRUD API "POST /Organization" endpoint with the following JSON body:
      """
      {
        "identifier_ODS_ODSCode": "DUPLICATE456",
        "name": "Second Organisation",
        "active": true,
        "type": "GP Practice",
        "telecom": []
      }
      """
    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "second_organisation_id"

    When I call the CRUD API "PUT /Organization/{{second_organisation_id}}" endpoint with the following JSON body:
      """
      {
        "id": "{{second_organisation_id}}",
        "resourceType": "Organization",
        "identifier": [
          {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "DUPLICATE123"
          }
        ],
        "name": "Updated Second Organisation",
        "active": true,
        "telecom": []
      }
      """

    # TODO: All of the following assertions are based on the existing functionality.
    # This is wrong and will need a bug raising.
    Then the response status code should be 200
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "information",
            "code": "success",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_UPDATED",
                  "display": "Existing resource updated"
                }
              ],
              "text": "Organisation updated successfully"
            },
            "diagnostics": "Organisation updated successfully"
          }
        ]
      }
      """

    When I call the CRUD API "GET /Organization/{{second_organisation_id}}" endpoint
    Then the response status code should be 200
    And the response body should contain the following JSON:
      """
      {
        "identifier_ODS_ODSCode": "DUPLICATE123"
      }
      """

  Scenario: Update an organisation with a no-op update
    When I call the CRUD API "POST /Organization" endpoint with the following JSON body:
      """
      {
        "identifier_ODS_ODSCode": "NOOP123",
        "name": "No-op Organisation",
        "active": true,
        "type": "GP Practice",
        "telecom": []
      }
      """
    Then the response status code should be 201
    And the "Location" header should be present in the response
    And the ID is extracted from the Location header as "organisation_id"
    And the "lastUpdated" value is extracted from the response body as "last_updated_time"

    When I call the CRUD API "PUT /Organization/{{organisation_id}}" endpoint with the following JSON body:
      """
      {
        "id": "{{organisation_id}}",
        "resourceType": "Organization",
        "identifier": [
          {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "NOOP123"
          }
        ],
        "name": "No-op Organisation",
        "active": true,
        "telecom": []
      }
      """
    Then the response status code should be 200

    # Another bug - this should be a no-op update and not update the lastUpdated timestamp. Will need raising and fixing.
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "information",
            "code": "success",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_UPDATED",
                  "display": "Existing resource updated"
                }
              ],
              "text": "Organisation updated successfully"
            },
            "diagnostics": "Organisation updated successfully"
          }
        ]
      }
      """

    When I call the CRUD API "GET /Organization/{{organisation_id}}" endpoint
    Then the response status code should be 200
  # TODO: Uncomment the following assertion and fix the underlying bug where a no-op update is still updating the lastUpdated timestamp.
  # And the "lastUpdated" field in the response body should be "{{last_updated_time}}"

  Scenario: Update an organisation with a non-existent ID
    When I call the CRUD API "PUT /Organization/00000000-0000-0000-0000-00000000000a" endpoint with the following JSON body:
      """
      {
        "id": "00000000-0000-0000-0000-00000000000a",
        "resourceType": "Organization",
        "identifier": [
          {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "NONEXIST123"
          }
        ],
        "name": "Non-existent Organisation",
        "active": true,
        "telecom": []
      }
      """

    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "not-found",
            "details": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                  "code": "MSG_NO_EXIST",
                  "display": "Resource does not exist"
                }
              ],
              "text": "Organisation not found."
            },
            "diagnostics": "Organisation not found."
          }
        ]
      }
      """



  Scenario: Update an organisation with an invalid ID format
    When I call the CRUD API "PUT /Organization/invalid-uuid-format" endpoint with the following JSON body:
      """
      {
        "id": "invalid-uuid-format",
        "resourceType": "Organization",
        "identifier": [
          {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "INVALID123"
          }
        ],
        "name": "Invalid Format Organisation",
        "active": true,
        "telecom": []
      }
      """
    Then the response status code should be 422
