import json
import logging
from django.db.models import Q

from autoreduce_db.reduction_viewer.models import ReductionRun, Status
from autoreduce_frontend.autoreduce_webapp.view_utils import (login_and_uows_valid, render_with, require_admin)
from autoreduce_frontend.utilities.pagination import CustomPaginator

LOGGER = logging.getLogger(__package__)


@require_admin
@login_and_uows_valid
@render_with('fail_queue.html')
# pylint:disable=no-member,too-many-locals,broad-except
def fail_queue(request):
    """Render status of failed queue."""
    # Render the page
    error_status = Status.get_error()
    failed_jobs = ReductionRun.objects.filter(Q(status=error_status)
                                              & Q(hidden_in_failviewer=False)).order_by('-created')
    if len(failed_jobs) == 0:
        return {'queue': []}

    max_items_per_page = request.GET.get('pagination', 10)
    custom_paginator = CustomPaginator(page_type='run',
                                       query_set=failed_jobs,
                                       items_per_page=max_items_per_page,
                                       page_tolerance=3,
                                       current_page=request.GET.get('page', 1))

    context_dictionary = {
        'queue': failed_jobs,
        'status_success': Status.get_completed(),
        'status_failed': Status.get_error(),
        'paginator': custom_paginator,
        'last_page_index': len(custom_paginator.page_list),
        'max_items': max_items_per_page
    }

    if request.method == 'POST':
        # Perform the specified action
        action = request.POST.get("action", "default")
        selected_run_string = request.POST.get("selectedRuns", [])
        selected_runs = json.loads(selected_run_string)
        try:
            for run in selected_runs:
                run_number = int(run[0])
                run_version = int(run[1])

                reduction_run = failed_jobs.get(run_number=run_number, run_version=run_version)

                if action == "hide":
                    reduction_run.hidden_in_failviewer = True
                    reduction_run.save()
                elif action == "default":
                    pass

        except Exception as exception:
            fail_str = "Selected action failed: %s %s" % (type(exception).__name__, exception)
            LOGGER.info("Failed to carry out fail_queue action - %s", fail_str)
            context_dictionary["message"] = fail_str

    return context_dictionary
