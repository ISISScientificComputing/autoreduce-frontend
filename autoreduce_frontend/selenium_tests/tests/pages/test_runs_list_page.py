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
from autoreduce_frontend.selenium_tests.tests.base_tests import NavbarTestMixin, BaseTestCase, FooterTestMixin, \
    AccessibilityTestMixin


class TestRunsListPage(NavbarTestMixin, BaseTestCase, FooterTestMixin, AccessibilityTestMixin):
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


class TestParameters(BaseTestCase):
    """Test cases for the InstrumentSummary page queries."""

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def test_page_num_query(self, page=None):
        """Test that the given page number is a query for the page."""
        # Launch the web page if no page arg supplied
        if not page:
            self.page.launch()
            page = 1

        # Evalutes to "page=<page>"
        page_query = f"page={page}"

        # Check if page query is in the href
        assert page_query in self.page.get_top_run().get_attribute('href')

        # Get the number of the top run
        top_run_num = int(self.page.get_top_run().text)

        # Click the top run and assign a RunSummaryPage object
        run_summary_page = self.page.click_run(top_run_num)

        # Check if the page query is in the url for the summary page
        assert page_query in run_summary_page.driver.current_url

        # Check if the page query is in the summary page href
        assert page_query in run_summary_page.cancel_button.get_attribute('href')

        # Click the cancel button to go back to the runs list
        run_summary_page.click_cancel_btn()

        # Check if page query is still in the href
        assert page_query in self.page.get_top_run().get_attribute('href')

    def test_second_page_num_query(self):
        """Test that the second page of runs passes the correct page number query."""
        self.page.launch()

        # Click the 'Next Page' button
        self.page.click_page("Next Page")

        # Test that the page number query works for the second page
        self.test_page_num_query(page=2)
