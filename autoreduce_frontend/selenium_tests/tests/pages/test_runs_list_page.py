# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""

import time
from autoreduce_qp.systemtests.utils.data_archive import DataArchive
from selenium.webdriver.support.wait import WebDriverWait
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (AccessibilityTestMixin, BaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


class TestRunsListPage(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    """Test cases for the InstrumentSummary page."""

    fixtures = BaseTestCase.fixtures + ["test_runs_list_page"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def test_reduction_run_displayed(self):
        """
        Test that run '99999' is displayed when the run exists in the database.
        """
        runs = self.page.launch().get_run_numbers_from_table()
        assert "99999" in runs

    def test_alert_message_when_missing_reduce_vars(self):
        """
        Test that the correct message is shown when the reduce_vars.py file is
        missing.
        """
        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py is missing for this instrument."
        assert self.page.alert_message_text() == expected

    def test_alert_message_when_reduce_vars_has_error(self):
        """
        Test that the correct message is shown when the reduce_vars.py has an
        error in it.
        """
        data_archive = DataArchive([self.instrument_name], 21, 21)
        data_archive.create()

        # add a reduce_vars script with a syntax error -> a missing " after value1
        data_archive.add_reduce_vars_script(self.instrument_name, """standard_vars={"variable1":"value1}""")

        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py has an import or syntax error."
        assert self.page.alert_message_text() == expected

        data_archive.delete()


class TestRunsListQueries(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    """Test cases for the InstrumentSummary page queries."""

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def _test_page_query(self, query):
        """
        Test that the given query is in a run's URL after clicking a run and
        then clicking the 'Back to <InstrumentName> runs' button.
        """
        assert query in self.page.get_top_run().get_attribute('href')

        # Check queries runs after clicking the top run
        top_run_num = int(self.page.get_top_run().text)
        run_summary_page = self.page.click_run(top_run_num)
        assert query in run_summary_page.driver.current_url
        assert query in run_summary_page.cancel_button.get_attribute('href')

        # Check queries after returning to runs list
        runs_list_page = run_summary_page.click_cancel_btn()
        assert query in runs_list_page.get_top_run().get_attribute('href')
        assert query in runs_list_page.driver.current_url

    def test_each_query(self):
        """Test that each potential query is maintained."""
        for query in ("sort=run", "pagination=10", "filter=run", "page="):
            self.page.launch()
            self._test_page_query(query + ("1" if query == "page=" else ""))

            self.page.click_page_by_title("Next Page")
            self._test_page_query(query + ("2" if query == "page=" else ""))

    def test_pagination_filter(self):
        """Test that changing the pagination filter also updates the URL query."""
        for pagination in (10, 25, 50, 100, 250, 500):
            self.page.launch()
            self.page.update_items_per_page_option(pagination)
            self.page.click_apply_filters()
            self._test_page_query(f"pagination={pagination}")

    def test_sort_by_filter(self):
        """Test that changing the sort by filter also updates the URL query."""
        for sort in ("number", "date"):
            self.page.launch()
            self.page.update_sort_by_option(sort.title())
            self.page.click_apply_filters()

            if sort == "number":
                sort = "run"

            self._test_page_query(f"sort={sort}")

    def test_run_navigation_btns(self):
        """Test that the run navigation buttons work."""
        for nav in ("newest", "next", "previous"):
            self.page.launch()
            runs = self.page.get_run_btns_by_cls_name("run-num-links")
            fifth_displayed_run = runs[4]
            run_summary_page = self.page.click_run(int(fifth_displayed_run.text))
            assert self.page.driver.title == "Reduction job #100005 - ISIS Auto-reduction"
            time.sleep(3)
            run_summary_page.driver.find_element_by_id(nav).click()
            run_summary_page.driver.refresh()
            time.sleep(3)
            if (nav == "next"):
                assert run_summary_page.title_text() == "Reduction Job #100006"
            elif (nav == "previous"):
                assert run_summary_page.title_text() == "Reduction Job #100004"
            elif (nav == "newest"):
                assert run_summary_page.title_text() == "Reduction Job #100009"
