# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Test cases for the manual job submission script
"""
import unittest
import __builtin__

from mock import patch

from scripts.manual_operations.manual_remove import ManualRemove
from utils.clients.database_client import DatabaseClient


# pylint:disable=invalid-name
class TestManualSubmission(unittest.TestCase):
    """
    Test manual_submission.py
    """
    def setUp(self):
        self.manual_remove = ManualRemove(instrument='GEM')
        # Setup database connection so it is possible to use
        # ReductionRun objects with valid meta data
        self.database_client = DatabaseClient()
        self.database_client.connect()

        # Fake ReductionRun objects for testing
        self.gem_object_1 = self.database_client.reduction_run()
        self.gem_object_1.run_number = '123'
        self.gem_object_1.run_name = 'first version of GEM123'
        self.gem_object_1.run_version = '1'

        self.gem_object_2 = self.database_client.reduction_run()
        self.gem_object_2.run_number = '123'
        self.gem_object_2.run_name = 'second version of GEM123'
        self.gem_object_2.run_version = '2'

    def test_find_run(self):
        """
        Check if a run exists in the database
        """
        actual = self.manual_remove.find_runs_in_database(run_number='001')
        self.assertEqual(2, len(actual))

    def test_find_run_invalid(self):
        """
        Check if a run does not exist in the database
        """
        actual = self.manual_remove.find_runs_in_database(run_number='000')
        expected = []
        self.assertEqual(expected, actual)

    @patch('scripts.manual_operations.manual_remove.ManualRemove.run_not_found')
    def test_process_results_not_found(self, mock_not_found):
        """
        Test process_results function routes to correct function if the run is not found
        """
        self.manual_remove.to_delete['123'] = []
        self.manual_remove.process_results()
        mock_not_found.assert_called_once()

    @patch('scripts.manual_operations.manual_remove.ManualRemove.multiple_versions_found')
    def test_process_results_multi(self, mock_multi_version):
        """
        Test process_results function routes to correct function if the run has multiple versions
        Note: for this test the content of results[key] list does not have to be Run objects
        """
        self.manual_remove.to_delete['123'] = ['test', 'test2']
        self.manual_remove.process_results()
        mock_multi_version.assert_called_once()

    def test_run_not_found(self):
        """
        Test that the corresponding key is deleted if the value if empty
        """
        self.manual_remove.to_delete['123'] = []
        self.manual_remove.run_not_found('123')
        self.assertEqual(0, len(self.manual_remove.to_delete))

    @patch('scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input')
    @patch.object(__builtin__, 'raw_input')
    def test_multiple_versions_found_single_input(self, mock_raw_input, mock_validate_csv):
        """
        Test that the user is not asked more than once for input if the input is valid
        """
        self.manual_remove.to_delete['123'] = [self.gem_object_1,
                                               self.gem_object_2]
        self.assertEqual(2, len(self.manual_remove.to_delete['123']))
        mock_raw_input.return_value = '2'
        mock_validate_csv.return_value = (True, [2])
        self.manual_remove.multiple_versions_found('123')
        # We said to delete version 2 so it should be the only entry for that run number
        self.assertEqual(1, len(self.manual_remove.to_delete['123']))
        self.assertEqual('2', self.manual_remove.to_delete['123'][0].run_version)

    @patch('scripts.manual_operations.manual_remove.ManualRemove.validate_csv_input')
    @patch.object(__builtin__, 'raw_input')
    def test_multiple_versions_found_list_input(self, mock_raw_input, mock_validate_csv):
        """
        Test that the user is not asked more than once for input if the input is valid
        """
        self.manual_remove.to_delete['123'] = [self.gem_object_1,
                                               self.gem_object_2]
        self.assertEqual(2, len(self.manual_remove.to_delete['123']))
        mock_raw_input.return_value = '1,2'
        mock_validate_csv.return_value = (True, [1, 2])
        self.manual_remove.multiple_versions_found('123')
        # We said to delete version 2 so it should be the only entry for that run number
        self.assertEqual(2, len(self.manual_remove.to_delete['123']))

    @patch('scripts.manual_operations.manual_remove.ManualRemove.delete_record')
    def test_delete_records(self, mock_delete):
        """
        Test that the correct query is sent to attempt to delete a record from the database
        """
        self.manual_remove.find_runs_in_database('1')
        self.assertEqual(2, len(self.manual_remove.to_delete['1']))
        del self.manual_remove.to_delete['1'][0]
        # have to use long as this is supported type in DB
        self.assertEqual(long(1), self.manual_remove.to_delete['1'][0].run_version)
        self.manual_remove.delete_records()
        self.assertEqual(0, len(self.manual_remove.to_delete))
        # Ensure that the delete functions were called on the expected tables
        mocked_delete_calls = mock_delete.call_args_list
        self.assertEqual(type(self.database_client.reduction_location()),
                         type(mocked_delete_calls[0][0][0]))
        self.assertEqual(type(self.database_client.reduction_data_location()),
                         type(mocked_delete_calls[1][0][0]))
        self.assertEqual(type(self.database_client.reduction_run()),
                         type(mocked_delete_calls[2][0][0]))

    def test_validate_csv_single_val(self):
        """
        Test user input validation
        """
        actual = self.manual_remove.validate_csv_input('1')
        self.assertEqual((True, [1]), actual)

    def test_validate_csv_list(self):
        """
        Test user input validation
        """
        actual = self.manual_remove.validate_csv_input('1,2,3')
        self.assertEqual((True, [1, 2, 3]), actual)

    def test_validate_csv_invalid(self):
        """
        Test user input validation
        """
        actual = self.manual_remove.validate_csv_input('t,e,s,t')
        self.assertEqual((False, []), actual)
