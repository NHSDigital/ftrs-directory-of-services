@is-infra @is-pipeline @data-repo
Feature: Data Repository

  Scenario: Retrieve organisation model from seeded repository
    Given I have a organisation repo that is seeded
    And I get a model with id "00000000-bab3-4baf-92da-0c77df9363a6" from the repo
    Then a model of type Organisation is returned
    And the model has an id of "00000000-bab3-4baf-92da-0c77df9363a6"
    And I save the model as a json file

  Scenario: Retrieve created model from repository
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/11111111-bab3-4baf-92da-0c77df9363a6.json"
    And I get a model with id "11111111-bab3-4baf-92da-0c77df9363a6" from the repo
    Then a model of type Organisation is returned
    And the model has an id of "11111111-bab3-4baf-92da-0c77df9363a6"

  Scenario: Retrieve non-existent model from repository
    Given I have a organisation repo
    Given I get a model with id "INVALID" from the repo
    Then the model is not returned

