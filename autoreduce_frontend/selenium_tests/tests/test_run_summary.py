# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Selenium tests for the runs summary page
"""

from django.urls import reverse
from autoreduce_db.reduction_viewer.models import ReductionRun
from autoreduce_qp.systemtests.utils.data_archive import DataArchive
from selenium.webdriver.support.wait import WebDriverWait

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase, FooterTestMixin, NavbarTestMixin


# pylint:disable=no-member
class TestRunSummaryPage(NavbarTestMixin, BaseTestCase, FooterTestMixin):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT visible
    """

    fixtures = BaseTestCase.fixtures + ["run_with_one_variable"]

    @classmethod
    def setUpClass(cls):
        """Sets up Dataarchive with scripts and sets instrument for all test cases"""
        super().setUpClass()
        cls.instrument_name = "TestInstrument"
        cls.data_archive = DataArchive([cls.instrument_name], 21, 21)
        cls.data_archive.create()
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")

    @classmethod
    def tearDownClass(cls) -> None:
        """Destroys created data archive"""
        cls.data_archive.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """Sets up RunSummaryPage before each test case"""
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 99999, 0)
        self.page.launch()

    def test_reduction_job_panel_displayed(self):
        """Tests that the reduction job panel is showing the right things"""
        # only one run in the fixture, get it for assertions
        run = ReductionRun.objects.first()
        assert self.page.reduction_job_panel.is_displayed()
        assert self.page.run_description_text() == f"Run description: {run.run_description}"
        # because it's started_by: -1, determined in `started_by_id_to_name`
        assert self.page.started_by_text() == "Started by: Development team"
        assert self.page.status_text() == "Status: Processing"
        assert self.page.instrument_text() == f"Instrument: {run.instrument.name}"
        assert self.page.rb_number_text() == f"RB Number: {run.experiment.reference_number}"
        assert self.page.last_updated_text() == "Last Updated: 19 Oct 2020, 6:35 p.m."
        assert self.page.reduction_host_text() == "Host: test-host-123"

    def test_reduction_job_panel_reset_to_values_first_used_for_run(self):
        """Test that the button to reset the variables to the values first used for the run works"""
        self.page.toggle_button.click()
        self.page.variable1_field = "the new value in the field"

        self.page.reset_to_initial_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field.get_attribute("value") == "value1"

    def test_reduction_job_panel_reset_to_current_reduce_vars(self):
        """Test that the button to reset the variables to the values from the reduce_vars script works"""
        self.page.toggle_button.click()
        self.page.variable1_field = "the new value in the field"

        self.page.reset_to_current_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field.get_attribute("value") == "test_variable_value_123"

    def test_rerun_form(self):
        """
        Test: Rerun form shows contents from Variable in database (from the fixture) and not reduce_vars.py
        """
        rerun_form = self.page.rerun_form
        assert not rerun_form.is_displayed()
        self.page.toggle_button.click()
        assert rerun_form.is_displayed()
        assert rerun_form.find_element_by_id("var-standard-variable1").get_attribute("value") == "value1"
        labels = rerun_form.find_elements_by_tag_name("label")

        WebDriverWait(self.driver, 10).until(lambda _: labels[0].text == "Re-run description")
        WebDriverWait(self.driver, 10).until(lambda _: labels[1].text == "variable1")

    def test_back_to_instruments_goes_back(self):
        """
        Test: Clicking back goes back to the instrument
        """
        back = self.page.cancel_button
        assert back.is_displayed()
        assert back.text == f"Back to {self.instrument_name} runs"
        back.click()
        assert reverse("runs:list", kwargs={"instrument": self.instrument_name}) in self.driver.current_url

    def test_reset_single_to_initial(self):
        """
        Tests changing the value of a variable field and resetting to the initial value, by using the inline button
        """
        self.page.toggle_button.click()
        initial_value = self.page.variable1_field_val
        self.page.variable1_field = "the new value in the field"
        assert self.page.variable1_field_val != initial_value

        self.page.variable1_field_reset_buttons.to_initial.click()
        assert self.page.variable1_field_val == initial_value

    def test_reset_single_to_script(self):
        """
        Tests changing the value of a variable field and resetting to the script value, by using the inline button
        """
        self.page.toggle_button.click()
        initial_value = "test_variable_value_123"
        self.page.variable1_field = "the new value in the field"
        assert self.page.variable1_field_val != initial_value

        self.page.variable1_field_reset_buttons.to_script.click()
        assert self.page.variable1_field_val == initial_value
