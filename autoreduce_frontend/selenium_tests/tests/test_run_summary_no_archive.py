# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Selenium tests for the runs summary page
"""

from autoreduce_db.reduction_viewer.models import ReductionRun

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase, FooterTestMixin, NavbarTestMixin, \
    AccessibilityTestMixin


# pylint:disable=no-member
class TestRunSummaryPageNoArchive(NavbarTestMixin, BaseTestCase, FooterTestMixin, AccessibilityTestMixin):
    fixtures = BaseTestCase.fixtures + ["run_with_one_variable"]

    @classmethod
    def setUpClass(cls):
        """Set the instrument for all test cases"""
        super().setUpClass()
        cls.instrument_name = "TestInstrument"

    def setUp(self) -> None:
        """Set up RunSummaryPage before each test case"""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 99999, 0)
        self.page.launch()

    def test_opening_run_summary_without_reduce_vars(self):
        """
        Test that opening the run summary without a reduce_vars present for the instrument
        will not show the "Reset to current" buttons as there is no current values!
        """
        # the reset to current values should not be visible
        assert self.page.warning_message.is_displayed()
        assert self.page.warning_message.text == ("The reduce_vars.py script is missing for this instrument."
                                                  " Please create it before being able to submit re-runs.")

    def test_opening_run_summary_without_run_variables(self):
        """
        Test that opening the run summary without a reduce_vars present for the instrument
        will not show the "Reset to current" buttons as there is no current values!
        """
        # Delete the variables, and re-open the page
        ReductionRun.objects.get(pk=1).run_variables.all().delete()
        self.page.launch()
        # the reset to current values should not be visible
        assert self.page.warning_message.is_displayed()
        assert self.page.warning_message.text == "No variables found for this run."
        assert self.page.run_description_text() == "Run description: This is the test run_description"
