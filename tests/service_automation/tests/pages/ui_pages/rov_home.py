"""
This module contains read only viewer home page objects
"""

from playwright.sync_api import Page


class HomePage:

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name="Read Only Viewer")
        self.Organisations_link = page.get_by_role("link", name="Organisations")
        self.Healthcare_Services_link = page.get_by_role("link", name="Healthcare Services")
        self.Locations_link = page.get_by_role("link", name="Locations")

    def load(self, url) -> None:
        self.page.goto(url)

    def click_organisations(self) -> None:
        self.Organisations_link.click()

    def click_healthcare_services(self) -> None:
        self.Healthcare_Services_link.click()

    def click_locations(self) -> None:
        self.Locations_link.click()

