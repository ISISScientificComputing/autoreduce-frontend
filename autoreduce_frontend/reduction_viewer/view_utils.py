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
from typing import Tuple

from next_prev import next_in_order, prev_in_order

from autoreduce_db.reduction_viewer.models import Instrument, ReductionRun
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from autoreduce_frontend.autoreduce_webapp.settings import DATA_ANALYSIS_BASE_URL

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


def get_run_navigation_queries(instrument_name: str, run: ReductionRun, page_type: str) -> Tuple[ReductionRun]:
    """Return a tuple of run navigation queries."""
    if page_type == "-run_number":
        order = '-run_number'
    elif page_type == "date":
        order = '-last_updated'

    instrument_obj = ReductionRun.objects.only('run_number').filter(instrument__name=instrument_name).order_by(order)

    next_run = prev_in_order(run, qs=instrument_obj)
    if next_run is None:
        next_run = run

    previous_run = next_in_order(run, qs=instrument_obj)
    if previous_run is None:
        previous_run = run

    newest_run = instrument_obj.first()
    oldest_run = instrument_obj.last()

    return next_run, previous_run, newest_run, oldest_run
