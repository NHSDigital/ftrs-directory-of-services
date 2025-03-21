"""
This module contains DuckDuckGoSearchPage,
the page object for the DuckDuckGo search page.
"""

from playwright.sync_api import Page


class UserTestLoginPage:

    URL = 'https://usertest.directoryofservices.nhs.uk/'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.mfa_help_link = page.locator('[href*="/app/controllers/mfa/mfa.php"]')

    def load(self) -> None:
        self.page.goto(self.URL)

    def search(self) -> None:
        self.mfa_help_link.click()
