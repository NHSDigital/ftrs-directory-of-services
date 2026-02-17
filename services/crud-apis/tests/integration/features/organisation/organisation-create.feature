@component
Feature: Organisations - Create Organisation

  As a user of the CRUD API
  I want to be able to create a new organisation
  So that I can manage my organisations in the directory of services

  Background:
    Given the CRUD API is running

  Scenario: Create a new organisation with valid data
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
    And the response body should contain the following JSON:
      """
      {
        "createdBy": {
          "type": "app",
          "value": "crud-integration-tests",
          "display": "CRUD API"
        },
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

  Scenario: Create an organisation with a duplicate ODS code
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

    When I call the CRUD API "POST /Organization" endpoint with the following JSON body:
      """
      {
        "identifier_ODS_ODSCode": "DUPLICATE123",
        "name": "Second Organisation",
        "active": true,
        "type": "GP Practice",
        "telecom": []
      }
      """
    Then the response status code should be 409
    And the response body should match the following JSON:
      """
      {
        "detail": "Organisation with this ODS code already exists"
      }
      """
