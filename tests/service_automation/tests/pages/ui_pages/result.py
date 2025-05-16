"""
This module contains DirectoryofServices,
the page object for the MFA FAQ page.
"""

from playwright.sync_api import Page


class UserTestMfaHelpPage:
    def __init__(self, page: Page) -> None:
        self.page = page
