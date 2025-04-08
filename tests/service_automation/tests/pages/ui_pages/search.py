"""
This module contains DirectoryofServices objects,
the login page.
"""

from playwright.sync_api import Page


class UserTestLoginPage:

    URL = 'https://www.directoryofservices.nhs.uk/'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.mfa_help_link = page.locator('[href*="/app/controllers/mfa/mfa.php"]')

    def load(self) -> None:
        self.page.goto(self.URL)

    def search(self) -> None:
        self.mfa_help_link.click()
