# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

import requests
from unittest.mock import Mock, patch

from autoreduce_qp.systemtests.utils.data_archive import DataArchive
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse

from autoreduce_frontend.reduction_viewer.views.configure_new_batch_run import PARSING_ERROR_MESSAGE, UNABLE_TO_CONNECT_MESSAGE, UNAUTHORIZED_MESSAGE
from autoreduce_frontend.selenium_tests.pages.configure_new_batch_run_page import ConfigureNewBatchRunsPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase


class TestConfigureNewBatchRunsPage(BaseTestCase):
    fixtures = BaseTestCase.fixtures + ["batch_run"]

    @classmethod
    def setUpClass(cls):
        """Sets up the data archive to be shared across test cases"""
        super().setUpClass()
        cls.instrument_name = "TESTINSTRUMENT"
        cls.data_archive = DataArchive([cls.instrument_name], 21, 21)
        cls.data_archive.create()
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")

    @classmethod
    def tearDownClass(cls) -> None:
        """Destroys the data archive"""
        cls.data_archive.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """Sets up the ConfigureNewRunsPage before each test case"""
        super().setUp()
        self.page = ConfigureNewBatchRunsPage(self.driver, self.instrument_name)
        self.page.launch()

    def _make_token(self):
        user_model = get_user_model()
        Token.objects.create(user=user_model.objects.get(username="super"))

    def test_reset_values_does_reset_the_values(self):
        """Test that the button to reset the variables to the values from the reduce_vars script works"""
        self.page.variable1_field = "the new value in the field"
        self.page.reset_to_current_values.click()

        # need to re-query the driver because resetting replaces the elements
        assert self.page.variable1_field_val == "test_variable_value_123"  # pylint:disable=no-member

    def test_back_to_instruments_goes_back(self):
        """
        Test: Clicking back goes back to the instrument
        """
        back = self.page.cancel_button
        assert back.is_displayed()
        assert back.text == "Cancel"
        back.click()
        assert reverse("runs:list", kwargs={"instrument": self.instrument_name}) in self.driver.current_url

    def test_submit_run_no_auth_token(self):
        """
        Test: Unauthorized user submitting a batch run is not allowed and shows an error message.
        """
        self.page.runs = "99999-100000"
        self.page.submit_button.click()
        assert self.page.error_text == UNAUTHORIZED_MESSAGE

    @patch("autoreduce_frontend.reduction_viewer.views.configure_new_batch_run.requests.post")
    def test_submit_run_post_non_200_status_code(self, requests_post: Mock):
        """
        Test: Render an error for a response with non-200 status code.
        """
        self._make_token()
        response = requests_post.return_value
        response.status_code = 400
        test_error_message = "test error message"
        response.content = f'{{"message": "{test_error_message}"}}'
        self.page.runs = "99999-100000"
        self.page.submit_button.click()
        assert self.page.error_text == test_error_message

    @patch("autoreduce_frontend.reduction_viewer.views.configure_new_batch_run.requests.post")
    def test_submit_run_post_bad_json(self, requests_post: Mock):
        """
        Test: Render an error for a response with non-200 status code.
        """
        self._make_token()
        response = requests_post.return_value
        response.status_code = 400
        response.content = "bad json"
        self.page.runs = "99999-100000"
        self.page.submit_button.click()
        assert self.page.error_text == PARSING_ERROR_MESSAGE.format("Expecting value: line 1 column 1 (char 0)",
                                                                    response.content)

    @patch("autoreduce_frontend.reduction_viewer.views.configure_new_batch_run.requests.post")
    def test_submit_run_post_raises_connection_error(self, requests_post: Mock):
        """
        Test: Render an error for a response with non-200 status code.
        """
        requests_post.side_effect = requests.exceptions.ConnectionError
        self._make_token()
        self.page.runs = "99999-100000"
        self.page.submit_button.click()
        assert self.page.error_text == UNABLE_TO_CONNECT_MESSAGE

    @patch("autoreduce_frontend.reduction_viewer.views.configure_new_batch_run.requests.post")
    def test_submit_run_post_raises_other_exc(self, requests_post: Mock):
        """
        Test: Render an error for a response with non-200 status code.
        """
        test_error_message = "test error message"
        requests_post.side_effect = Exception(test_error_message)
        self._make_token()
        self.page.runs = "99999-100000"
        self.page.submit_button.click()
        assert self.page.error_text == test_error_message
