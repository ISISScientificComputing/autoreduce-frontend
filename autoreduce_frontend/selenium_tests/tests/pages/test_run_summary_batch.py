# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.pages.test_run_summary import TestRunSummaryPage


# pylint:disable=no-member
class TestBatchRunSummaryPage(TestRunSummaryPage):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT
    visible.
    """

    fixtures = TestRunSummaryPage.fixtures + ["batch_run_with_one_variable"]

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case."""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 2, 0, batch_run=True)
        self.page.launch()

    def test_non_existent_run(self):
        """
        Test that going to the run summary for a non-existent run will redirect
        back to the runs list page and show a warning message to the user.
        """
        self.page = RunSummaryPage(self.driver, self.instrument_name, 12345, 0, batch_run=True)
        self.page.launch()
        self.driver.get(f"{self.driver.current_url}&filter=batch_runs")
        self.page = RunsListPage(self.driver, self.instrument_name)

        assert self.page.top_alert_message_text == 'Run 12345-0 does not exist. '\
                                                   'Redirected to the instrument page.'
