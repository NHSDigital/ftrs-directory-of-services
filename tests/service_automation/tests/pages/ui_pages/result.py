"""
This module contains DirectoryofServices,
the page object for the new account page.
"""

from playwright.sync_api import Page
from typing import List


class NewAccountPage:

    def __init__(self, page: Page) -> None:
        self.page = page
