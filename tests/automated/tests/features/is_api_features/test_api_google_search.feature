Feature: API Search Playwringht in Google

Scenario: API Search for Playwright in Google
  Given I make GET request to the Google search API
  When I receive the response
  Then I should see search results
