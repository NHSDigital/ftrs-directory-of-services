Feature: Google search API behavior

Scenario: API Search for Playwright in Google
  given I make GET request to the Google search API
  when I receive the response
  then I should see search results