# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Module for the search runs page model."""
from typing import List

from django.urls import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage


class SearchPage(Page, NavbarMixin, FooterMixin):
    def __init__(self, driver, instrument):
        super().__init__(driver)
        self.instrument = instrument

    @staticmethod
    def url_path():
        """
        Return the path section of the overview page url
        :return: (str) Path section of the page url
        """
        return reverse("search")

    @property
    def run_number_text_area(self) -> WebElement:
        return self.driver.find_element_by_id("id_run_number")

    @property
    def run_instrument_dropdown(self) -> WebElement:
        dropdown = Select(self.driver.find_element_by_id('id_instrument'))
        return dropdown

    @property
    def run_description_text_area(self) -> WebElement:
        return self.driver.find_element_by_id("id_run_description")

    @property
    def created_min_date(self) -> WebElement:
        created_min = self.driver.find_element_by_id("id_created_0")
        return created_min

    @property
    def created_max_date(self) -> WebElement:
        created_max = self.driver.find_element_by_id("id_created_1")
        return created_max

    @property
    def run_description_contains(self) -> WebElement:
        contains_radio_button = self.driver.find_element_by_xpath("//*[@id='contains']")
        return contains_radio_button

    @property
    def run_description_exact(self) -> WebElement:
        exact_radio_button = self.driver.find_element_by_xpath("//*[@id='exact']")
        return exact_radio_button

    def click_runs_tab(self) -> None:
        runs_tab = self.driver.find_element_by_class_name("runs-tab")
        runs_tab.click()

    def click_experiments_tab(self) -> None:
        experiments_tab = self.driver.find_element_by_class_name("experiments-tab")
        experiments_tab.click()

    def alert_runs_message_text(self) -> str:
        """
        Return the text of the alert message element with the id
        'run_message'.
        """
        return self.driver.find_element_by_id("run_message").text.strip()

    def alert_experiments_message_text(self) -> str:
        """
        Return the text of the alert message element with the id
        'experiment_message'.
        """
        return self.driver.find_element_by_id("experiment_message").text.strip()

    def get_run_numbers_from_table(self) -> List[str]:
        """
        Return the list of run numbers visible on the current table of the
        instrument summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements_by_class_name("run-num-links")]

    def click_search_button(self) -> None:
        """Click the `Search` button."""
        search_btn = self.driver.find_element_by_id("search-button")
        search_btn.click()

    def click_run(self, run_number: int, version: int = 0) -> RunSummaryPage:
        """
        Click a run and return the page object of its run summary.
        Args:
            run_number: Run number of the link to click.
            version: Version of the run to click.
        Returns:
            The page object of the opened run summary.
        """
        runs = self.driver.find_elements_by_xpath("//div[@class='table-container']/table/tbody/tr/td/a")
        run_string = f"{run_number} - {version}" if version else f"{run_number}"
        for run in runs:
            if run.text == run_string:
                run.click()
                return RunSummaryPage(self.driver, self.instrument, run_number, version)

        raise NoSuchElementException
