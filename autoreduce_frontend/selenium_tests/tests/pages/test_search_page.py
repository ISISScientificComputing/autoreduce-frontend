# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the search runs page."""

from autoreduce_frontend.selenium_tests.pages.search_page import SearchPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (
    NavbarTestMixin,
    BaseTestCase,
    FooterTestMixin,
)


class TestSearchPage(NavbarTestMixin, BaseTestCase, FooterTestMixin):
    """Test cases for the search runs page."""

    fixtures = BaseTestCase.fixtures + ["pr_test"]

    def setUp(self) -> None:
        """
        Sets up the HelpPage object
        """
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = SearchPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_alert_message_when_no_results(self):
        """
        Test that the correct message is shown when there are no results for the search
        """
        self.page.launch()
        expected = "Sorry, no runs found for this criteria."
        assert self.page.alert_message_text() == expected

    def test_search_by_run_number(self):
        self.page.launch()
        self.page.run_number_text_area.send_keys("99999")
        self.page.run_number_text_area.submit()
        runs = self.page.get_run_numbers_from_table()
        top_run = runs[0]
        run_summary_page = self.page.click_run(top_run)
        assert run_summary_page.driver.title == "Reduction job #99999 - ISIS Auto-reduction"

    def test_search_by_instrument(self):
        self.page.launch()
        dropdown = self.page.run_instrument_dropdown
        dropdown.select_by_visible_text("TestInstrument")
        self.page.click_search_button()
        runs = self.page.get_run_numbers_from_table()
        assert len(runs) != 0

    def test_created_date_selection(self):
        min_datefield = self.page.created_min_date
        max_datefield = self.page.created_max_date
        min_datefield.send_keys("01012011")
        max_datefield.send_keys("01012021")
        self.page.click_search_button()
        runs = self.page.get_run_numbers_from_table()
        assert len(runs) != 0

    def test_combining_queries(self):
        self.page.run_number_text_area.send_keys("99999")
        dropdown = self.page.run_instrument_dropdown
        dropdown.select_by_visible_text("TestInstrument")
        min_datefield = self.page.created_min_date
        max_datefield = self.page.created_max_date
        min_datefield.send_keys("01012011")
        max_datefield.send_keys("01012021")
        self.page.click_search_button()
        runs = self.page.get_run_numbers_from_table()
        assert len(runs) != 0

    def test_search_description(self):
        self.page.launch()
        self.page.run_description_text_area.send_keys("test run_description")
        self.page.run_description_contains.click()
        self.page.run_description_text_area.submit()
        runs = self.page.get_run_numbers_from_table()
        assert len(runs) != 0

    def test_search_description_exact(self):
        self.page.launch()
        self.page.run_description_text_area.send_keys("test run_description")
        self.page.run_description_exact.click()
        self.page.run_description_text_area.submit()
        runs = self.page.get_run_numbers_from_table()
        assert len(runs) == 0
