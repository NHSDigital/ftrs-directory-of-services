"""
This module contains read only viewer home page objects
"""

from playwright.sync_api import Page


class OrganisationsPage:

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name="Organisations")
        self.home_link = page.get_by_label("Breadcrumb").get_by_role("link", name="Home")
        self.name_heading = page.get_by_role("columnheader", name="Name")
        self.odscode_heading = page.get_by_role("columnheader", name="ODS Code")
        # page.get_by_role("cell", name="FKF73").click()
        # page.get_by_role("link", name="PAYDENS PHARMACY").click()

    def click_home_link(self) -> None:
        self.home_link.click()

