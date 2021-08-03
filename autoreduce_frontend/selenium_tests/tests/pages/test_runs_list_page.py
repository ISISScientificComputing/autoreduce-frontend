# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Selenium tests for the runs summary page
"""

from autoreduce_qp.systemtests.utils.data_archive import DataArchive
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (AccessibilityTestMixin, BaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


class TestRunsListPage(BaseTestCase, NavbarTestMixin, FooterTestMixin, AccessibilityTestMixin):
    """
    Test cases for the InstrumentSummary page
    """

    fixtures = BaseTestCase.fixtures + ["test_runs_list_page"]

    def setUp(self) -> None:
        """
        Sets up the InstrumentSummaryPage object
        """
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def test_reduction_run_displayed(self):
        """
        Test: Reduction run is displayed
        When: The run exists in the database
        """
        runs = self.page.launch().get_run_numbers_from_table()
        assert "99999" in runs

    def test_alert_message_when_missing_reduce_vars(self):
        """
        Test that the correct message is shown when the reduce_vars.py file is missing
        """
        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py is missing for this instrument."
        assert self.page.alert_message_text() == expected

    def test_alert_message_when_reduce_vars_has_error(self):
        """
        Test that the correct message is shown when the reduce_vars.py has an error in it
        """
        data_archive = DataArchive([self.instrument_name], 21, 21)
        data_archive.create()

        # add a reduce_vars script with a syntax error -> a missing " after value1
        data_archive.add_reduce_vars_script(self.instrument_name, """standard_vars={"variable1":"value1}""")

        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py has an import or syntax error."
        assert self.page.alert_message_text() == expected

        data_archive.delete()


class TestParameters(BaseTestCase, NavbarTestMixin, FooterTestMixin, AccessibilityTestMixin):
    """Test cases for the InstrumentSummary page queries."""

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def _test_page_query(self, query, page=None):
        """Test that the given query is in a run's URL after clicking a run and then clicking the 'Back to
        <InstrumentName> runs' button."""
        # Launch the web page if no page arg supplied
        if not page:
            self.page.launch()
            page = 1

        # Check if page query is in the href
        assert query in self.page.get_top_run().get_attribute('href')

        # Get the number of the top run
        top_run_num = int(self.page.get_top_run().text)

        # Click the top run and assign a RunSummaryPage object
        run_summary_page = self.page.click_run(top_run_num)

        # Check if the query is in the url for the summary page
        assert query in run_summary_page.driver.current_url

        # Check if the query is in the summary page href
        assert query in run_summary_page.cancel_button.get_attribute('href')

        # Click the cancel button to go back to the runs list
        run_summary_page.click_cancel_btn()

        # Check if query is still in the href
        assert query in self.page.get_top_run().get_attribute('href')

    def test_each_query(self):
        """Test that each potential query is maintained."""
        for query in ("sort=run", "pagination=10", "filter=run", "page="):
            self.page.launch()
            self._test_page_query(query + "1" if query == "page=" else "", page=1)
            self.page.click_page("Next Page")
            self._test_page_query(query + "2" if query == "page=" else "", page=2)

    def test_pagination_filter(self):
        """Test that changing the pagination filter also updates the URL query."""
        for pagination in (10, 25, 50, 100, 250, 500):
            self.page.launch()
            self.page.update_items_per_page_option(pagination)
            self.page.click_apply_filters()
            self._test_page_query(f"pagination={pagination}", page=1)

    def test_sort_by_filter(self):
        """Test that changing the sort by filter also updates the URL query."""
        for sort in ("number", "date"):
            self.page.launch()
            self.page.update_sort_by_option(sort.title())
            self.page.click_apply_filters()

            if sort == "number":
                sort = "run"

            # {sort=!s} resolves to 'sort=<sort>'
            self._test_page_query(f"sort={sort}", page=1)
