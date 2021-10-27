# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Utility functions for the reduction viewer models

Note: This file has a large number of pylint disable as it was un unit tested
at the time of fixing the pylint issues. Once unit tested properly, these disables
should be able to be removed. Many are relating to imports
"""
import time

from autoreduce_utils.clients.queue_client import QueueClient


class ScriptUtils:
    """
    Utilities for the scripts field
    """
    @staticmethod
    def get_reduce_scripts(scripts):
        """
        Returns a tuple of (reduction script, reduction vars script),
        each one a string of the contents of the script, given a list of script objects.
        """
        script_out = None
        script_vars_out = None
        for script in scripts:
            if script.file_name == "reduce.py":
                script_out = script
            elif script.file_name == "reduce_vars.py":
                script_vars_out = script
        return script_out, script_vars_out

    def get_cache_scripts_modified(self, scripts):
        """
        :returns: The last time the scripts in the database were
        modified (in seconds since epoch).
        """
        script_modified = None
        script_vars_modified = None

        for script in scripts:
            if script.file_name == "reduce.py":
                script_modified = self._convert_time_from_string(str(script.created))
            elif script.file_name == "reduce_vars.py":
                script_vars_modified = self._convert_time_from_string(str(script.created))
        return script_modified, script_vars_modified

    @staticmethod
    def _convert_time_from_string(string_time):
        """
        :return: time as integer for epoch
        """
        time_format = "%Y-%m-%d %H:%M:%S"
        string_time = string_time[:string_time.find('+')]
        return int(time.mktime(time.strptime(string_time, time_format)))


class MessagingUtils:
    """
    Utilities for sending messages to ActiveMQ
    """
    @staticmethod
    def send(message):
        """ Sends message to ReductionPending (with the specified delay) """
        message_client = QueueClient()
        message_client.connect()

        message_client.send('/queue/DataReady', message, priority='1')
        message_client.disconnect()
