"""
This module contains DirectoryofServices objects,
the login page.
"""

from playwright.sync_api import Page


class LoginPage:

    URL = 'https://www.directoryofservices.nhs.uk/'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.new_account_link = page.get_by_role("link", name="Request an account")

    def load(self) -> None:
        self.page.goto(self.URL)

    def search(self) -> None:
        self.new_account_link.click()
