# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from django.template import Library
from django.urls import reverse

register = Library()


@register.simple_tag
def get_run_navigation_queries(run_number: int, page: int, newest_run: int, oldest_run: int) -> str:
    """Return a string of run queries."""
    return (f"page={page}&newest_run={newest_run}&next_run={run_number+1}&"
            f"previous_run={run_number-1}&oldest_run={oldest_run}")


@register.simple_tag
def make_summary_url(batch_run: bool, instrument_name: str, run_number: int, run_version: int):
    """Reverses the URL taking into account whether to return for a batch run or a normal run."""
    if batch_run:
        return reverse("runs:batch_summary",
                       kwargs={
                           "instrument_name": instrument_name,
                           "pk": run_number,
                           "run_version": run_version
                       })
    else:
        return reverse("runs:summary",
                       kwargs={
                           'instrument_name': instrument_name,
                           'run_number': run_number,
                           'run_version': run_version
                       })
