# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Utility functions for the view of django models."""
# pylint:disable=no-member
import functools
import logging
import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import url_has_allowed_host_and_scheme
from autoreduce_db.reduction_viewer.models import Instrument
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from autoreduce_frontend.autoreduce_webapp.settings import DATA_ANALYSIS_BASE_URL

from autoreduce_frontend.autoreduce_webapp.settings import (ALLOWED_HOSTS, UOWS_LOGIN_URL)

LOGGER = logging.getLogger(__package__)


def deactivate_invalid_instruments(func):
    """Deactivate instruments if they are invalid."""
    @functools.wraps(func)
    def request_processor(request, *args, **kws):
        """
        Function decorator that checks the reduction script for all active
        instruments and deactivates any that cannot be found.
        """
        instruments = Instrument.objects.all()
        for instrument in instruments:
            script_path = ReductionScript(instrument.name)
            if instrument.is_active != script_path.exists():
                instrument.is_active = script_path.exists()
                instrument.save(update_fields=['is_active'])

        return func(request, *args, **kws)

    return request_processor


def get_interactive_plot_data(plot_locations):
    """Get the data for the interactive plots from the saved JSON files."""
    json_files = [location for location in plot_locations if location.endswith(".json")]

    output = {}
    for filepath in json_files:
        name = os.path.basename(filepath)
        with open(filepath, 'r') as file:
            data = file.read()
        output[name] = data

    return output


def make_data_analysis_url(reduction_location: str) -> str:
    """
    Makes a URL for the data.analysis website that will open the location of the
    data.
    """
    if "/instrument/" in reduction_location:
        return DATA_ANALYSIS_BASE_URL + reduction_location.split("/instrument/")[1]
    return ""


def windows_to_linux_path(path: str) -> str:
    """Convert Windows path to Linux path."""
    # '\\isis\inst$\' maps to '/isis/'
    path = path.replace(r'\\isis\inst$' + '\\', '/isis/')
    path = path.replace('\\', '/')
    return path


def linux_to_windows_path(path: str) -> str:
    """Convert Linux path to Windows path."""
    # '\\isis\inst$\' maps to '/isis/'
    path = path.replace('/isis/', r'\\isis\inst$' + '\\')
    path = path.replace('/', '\\')
    return path


def started_by_id_to_name(started_by_id=None):
    """
    Return the name of the user or team that submitted an autoreduction run.

    Args:
        started_by_id: The ID of the user who started the run, or a control code
        if not started by a user.

    Returns:
        If started by a valid user, return '[forename] [surname]'.

        If started automatically, return 'Autoreducton service'.

        If started manually, return 'Development team'.

        Otherwise, return None.
    """
    if started_by_id is None or started_by_id < -1:
        return None

    if started_by_id == -1:
        return "Development team"

    if started_by_id == 0:
        return "Autoreduction service"

    try:
        user = get_user_model()
        user_record = user.objects.get(id=started_by_id)
        return f"{user_record.first_name} {user_record.last_name}"
    except ObjectDoesNotExist as exception:
        LOGGER.error(exception)
        return None


def make_return_url(request, next_url):
    """
    Make the return URL based on whether a next_url is present in the url. If
    there is a next_url, verify that the url is safe and allowed before using
    it. If not, default to the host.
    """
    if next_url:
        if url_has_allowed_host_and_scheme(next_url, ALLOWED_HOSTS, require_https=True):
            return UOWS_LOGIN_URL + request.build_absolute_uri(next_url)
        else:
            # The next_url was not safe so don't use it - build from
            # request.path to ignore GET parameters
            return UOWS_LOGIN_URL + request.build_absolute_uri(request.path)
    else:
        return UOWS_LOGIN_URL + request.build_absolute_uri()
