# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the instrument summary page model
"""
from typing import List

from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.page import Page
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage


class RunsListPage(Page, NavbarMixin, FooterMixin, TourMixin):
    """
    Page model class for instrument summary page
    """
    def __init__(self, driver, instrument):
        super().__init__(driver)
        self.instrument = instrument

    def url_path(self):
        """
        Return the path section of the instrument url
        :return: (str) Path section of the page url
        """
        return reverse("runs:list", kwargs={"instrument": self.instrument})

    def get_run_numbers_from_table(self) -> List[str]:
        """
        Get the list of run numbers visible on the current table of the instrument summary page
        :return: (List) List of strings of the run numbers of the current instrument summary page
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements_by_class_name("run-num-links")]

    def click_run(self, run_number: int, version: int = 0) -> RunSummaryPage:
        """
        Click the run number link on the instrument summary table matching the given run number and
        version
        :param run_number: (int) the run number of the link to click
        :param version: (int) the version of the run to click
        :return: (RunSummaryPage) The page object of the opened run summary page.
        """
        runs = self.driver.find_elements_by_class_name("run-num-links")
        run_string = f"{run_number} - {version}" if version else f"{run_number}"
        for run in runs:
            if run.text == run_string:
                run.click()
                return RunSummaryPage(self.driver, self.instrument, run_number, version)
        raise NoSuchElementException

    def alert_message_text(self) -> str:
        """Get the the from the alert message"""
        return self.driver.find_element_by_id("alert_message").text.strip()

    def get_top_run(self) -> None:
        """Get the top run using the element's id."""
        return self.driver.find_element_by_id("top-run-number")

    def click_page_by_title(self, title: str) -> None:
        """Click the page navigation button matching the given title."""
        btns = self.driver.find_elements_by_tag_name("button")

        for btn in btns:
            if btn.get_attribute("title") == title:
                btn.click()
                break
        else:
            raise NoSuchElementException

    def update_items_per_page_option(self, pagination: int) -> None:
        """
        Select the supplied pagination option from the 'Items per page' combo
        box.
        """
        pagination_select = Select(self.driver.find_element_by_id("pagination_select"))
        pagination_select.select_by_visible_text(str(pagination))

    def update_sort_by_option(self, sort_by: str) -> None:
        """Select the supplied sort by option from the 'Sort by' combo box."""
        pagination_select = Select(self.driver.find_element_by_id("sort_select"))
        pagination_select.select_by_visible_text(sort_by)

    def click_apply_filters(self) -> None:
        "Click the 'Apply filters' button."
        btn = self.driver.find_element_by_id("apply_filters")
        btn.click()

    def get_run_btns_by_cls_name(self, cls_name: str) -> None:
        """Return all elements containing the specified class name."""
        return self.driver.find_elements_by_class_name(cls_name)
