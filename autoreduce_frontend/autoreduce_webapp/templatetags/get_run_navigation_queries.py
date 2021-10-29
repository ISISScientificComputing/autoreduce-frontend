# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from django.template import Library
from django.urls import reverse
from typing import Tuple
from autoreduce_db.reduction_viewer.models import ReductionRun
from next_prev import next_in_order, prev_in_order

register = Library()


@register.simple_tag
def get_run_navigation_queries(instrument_name: str,
                               run: ReductionRun,
                               page_type: str,
                               run_unique_id: int = None) -> Tuple[ReductionRun]:
    """Return a string of run queries."""

    if run.batch_run:
        next_run = run_unique_id
        previous_run = run_unique_id
        first_run = run_unique_id
        last_run = run_unique_id
        return next_run, previous_run, first_run, last_run

    else:
        instrument_obj = ReductionRun.objects.filter(instrument__name=instrument_name).order_by('-pk', 'run_version')
        next_run = prev_in_order(run, qs=instrument_obj)
        if next_run is None:
            next_run = run

        previous_run = next_in_order(run, qs=instrument_obj)
        if previous_run is None:
            previous_run = run

        newest_run = instrument_obj.first()
        oldest_run = instrument_obj.last()
        first_run = newest_run.run_number
        last_run = oldest_run.run_number
        return next_run, previous_run, first_run, last_run


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
