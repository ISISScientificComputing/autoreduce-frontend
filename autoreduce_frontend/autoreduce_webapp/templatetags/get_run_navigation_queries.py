# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from autoreduce_db.reduction_viewer.models import ReductionRun
from next_prev import next_in_order, prev_in_order
from django.template import Library
from django.urls import reverse

register = Library()


@register.simple_tag
def get_run_navigation_queries(run_number: int,
                               page: int,
                               newest_run: int,
                               oldest_run: int,
                               instrument_name=None,
                               page_type="run") -> str:
    """Return a string of run queries."""
    next_run = None
    previous_run = None
    if (page_type == "run"):
        order = '-run_number'
    elif (page_type == "date"):
        order = '-last_updated'
    try:
        instrument_obj = ReductionRun.objects.filter(instrument__name=instrument_name, batch_run=False).order_by(order)
        r = instrument_obj.get(run_number=run_number)
        next_run = prev_in_order(r, qs=instrument_obj, loop=True)
        previous_run = next_in_order(r, qs=instrument_obj, loop=True)
        if next_run == None:
            next_run = r.run_number
        if previous_run == None:
            previous_run = r.run_number
        newest_run = str(newest_run).partition(":")[0]
        oldest_run = str(oldest_run).partition(":")[0]
    except Exception:  # pylint:disable=broad-except
        print("Error has occured fetching next and previous models for navigation.")
        newest_run = str(newest_run).partition(":")[0]
        oldest_run = str(oldest_run).partition(":")[0]

    return (f"page={page}&newest_run={newest_run}&next_run={next_run}&"
            f"previous_run={previous_run}&oldest_run={oldest_run}")


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
