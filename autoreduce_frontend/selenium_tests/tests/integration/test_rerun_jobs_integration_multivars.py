# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

import tempfile

from autoreduce_frontend.selenium_tests.pages.rerun_jobs_page import RerunJobsPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseIntegrationTestCase
from autoreduce_frontend.selenium_tests.utils import submit_and_wait_for_result

TEMP_OUT_FILE = tempfile.NamedTemporaryFile()  # pylint:disable=consider-using-with
SCRIPT = f"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

import reduce_vars as web_var

def main(input_file, output_dir):
    with open("{TEMP_OUT_FILE.name}", 'w+') as file:
        file.write("\\n".join([str(var) for var in web_var.standard_vars.items()]))
"""


class TestRerunJobsPageIntegrationMultiVar(BaseIntegrationTestCase):
    fixtures = BaseIntegrationTestCase.fixtures + ["run_with_multiple_variables"]

    @classmethod
    def setUpClass(cls):
        """Starts external services and sets instrument for all test cases"""
        super().setUpClass()
        cls.data_archive.add_reduction_script(cls.instrument_name, SCRIPT)
        cls.data_archive.add_reduce_vars_script(
            cls.instrument_name, """standard_vars={"variable_str":"test_variable_value_123",
                                                "variable_int":123, "variable_float":123.321,
                                                "variable_listint":[1,2,3], "variable_liststr":["a","b","c"],
                                                "variable_none":None, "variable_empty":"", "variable_bool":True}""")

    def setUp(self) -> None:
        """Sets up RerunJobsPage before each test case"""
        super().setUp()
        self.page = RerunJobsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_submit_rerun_same_variables(self):
        """
        Test: Just opening the submit page and clicking rerun
        """
        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments

    def test_submit_rerun_changed_variable_arbitrary_value(self):
        """
        Test: Open submit page, change a variable, submit the run
        """
        new_str_value = "the new value in the field"
        self.page.variable_str_field = new_str_value
        new_int = "42"
        self.page.variable_int_field = new_int
        new_float = "144.33"
        self.page.variable_float_field = new_float
        new_listint = "[111, 222]"
        self.page.variable_listint_field = new_listint
        new_liststr = "['string1', 'string2']"
        self.page.variable_liststr_field = new_liststr
        new_bool = "False"
        self.page.variable_bool_field = new_bool

        result = submit_and_wait_for_result(self)
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments != result[1].arguments

        args = result[1].arguments.as_dict()
        assert args["standard_vars"]["variable_str"] == new_str_value
        assert args["standard_vars"]["variable_int"] == new_int
        assert args["standard_vars"]["variable_float"] == new_float
        assert args["standard_vars"]["variable_listint"] == new_listint
        assert args["standard_vars"]["variable_liststr"] == new_liststr
        assert args["standard_vars"]["variable_none"] == "None"
        assert args["standard_vars"]["variable_empty"] == ""
        assert args["standard_vars"][
            "variable_bool"] == False  # FIXME: for some reason the POST form isn't reading the correct True/False value anymore!?

        # The SCRIPT has saved out the variable values to a temporary file - read it back in
        # and check that they match what was saved in the arguments
        with open(TEMP_OUT_FILE.name, 'r') as fil:
            contents = fil.read()

        for name, value in args["standard_vars"].items():
            assert name in contents
            assert str(value) in contents
