@component
Feature: Organisations - Delete Organisation

  As a user of the CRUD API
  I want to be able to delete an existing organisation
  So that I can remove organisations from the directory of services when they are no longer relevant

  Background:
    Given the CRUD API is running

  Scenario: Delete an organisation
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

    When I call the CRUD API "DELETE /Organization/{{organisation_id}}" endpoint
    Then the response status code should be 204
    And the response body should be empty

    When I call the CRUD API "GET /Organization/{{organisation_id}}" endpoint
    Then the response status code should be 404

  Scenario: Delete an organisation with a non-existent ID
    When I call the CRUD API "DELETE /Organization/00000000-0000-0000-0000-00000000000a" endpoint
    Then the response status code should be 404
    And the response body should match the following JSON:
      """
      {
        "detail": "Organisation not found"
      }
      """

  Scenario: Delete an organisation with an invalid ID format
    When I call the CRUD API "DELETE /Organization/invalid-uuid-format" endpoint
    Then the response status code should be 422
