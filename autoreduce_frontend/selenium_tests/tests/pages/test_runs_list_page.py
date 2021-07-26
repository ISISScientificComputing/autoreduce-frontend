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

from autoreduce_frontend.selenium_tests.utils import setup_archive


class TestRunsListPage(BaseTestCase):
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


class TestNew(BaseTestCase):
    """
    Test cases for the InstrumentSummary page
    """

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """
        Sets up the InstrumentSummaryPage object
        """
        super().setUp()
        self.instrument_name = "TestInstrument"
        self.page = RunsListPage(self.driver, self.instrument_name)

        #self.data_archive = setup_archive([self.instrument_name], 21, 21)
        #self.data_archive.add_reduce_vars_script(self.instrument_name, 'standard_vars = {"variable": "somevalue"}')

    def test_page_param_in_href(self):
        """
        Test that the page parameter is within the href
        """
        self.page.launch()
        assert "page=1" in self.page.get_top_run().get_attribute('href')
        run_summary_page = self.page.click_run(100000)
        assert "page=1" in run_summary_page.driver.current_url
        assert "page=1" in run_summary_page.cancel_button.get_attribute('href')
        run_summary_page.click_cancel_btn()
        assert "page=1" in self.page.get_top_run().get_attribute('href')
