import traceback
import logging

from autoreduce_db.reduction_viewer.models import Experiment, Instrument, ReductionRun, Status
from autoreduce_qp.queue_processor.variable_utils import VariableUtils
from autoreduce_frontend.autoreduce_webapp.view_utils import check_permissions, login_and_uows_valid, render_with

from autoreduce_frontend.utilities.pagination import CustomPaginator

LOGGER = logging.getLogger(__package__)


@login_and_uows_valid
@check_permissions
@render_with('runs_list.html')
# pylint:disable=no-member,unused-argument,too-many-locals,broad-except
def runs_list(request, instrument=None):
    """Render instrument summary."""
    try:
        filter_by = request.GET.get('filter', 'run')
        instrument_obj = Instrument.objects.get(name=instrument)
    except Instrument.DoesNotExist:
        return {'message': "Instrument not found."}

    sort_by = request.GET.get('sort', 'run')

    try:
        runs = ReductionRun.objects.only('status', 'last_updated', 'run_version',
                                         'run_description').select_related('status').filter(instrument=instrument_obj,
                                                                                            batch_run=False)
        last_instrument_run = runs.filter(batch_run=False).last()
        first_instrument_run = runs.filter(batch_run=False).first()

        if sort_by == "run":
            runs = runs.order_by('-run_numbers__run_number', 'run_version')
        elif sort_by == "date":
            runs = runs.order_by('-last_updated')

        if len(runs) == 0:
            return {'message': "No runs found for instrument."}

        current_variables = {}
        try:
            current_variables.update(VariableUtils.get_default_variables(instrument_obj.name))
        except FileNotFoundError:
            error_reason = "reduce_vars.py is missing for this instrument"
        except (ImportError, SyntaxError):
            error_reason = "reduce_vars.py has an import or syntax error"
        else:
            error_reason = ""

        context_dictionary = {
            'instrument': instrument_obj,
            'instrument_name': instrument_obj.name,
            'runs': runs,
            'last_instrument_run': last_instrument_run,
            'first_instrument_run': first_instrument_run,
            'processing': runs.filter(status=Status.get_processing(), batch_run=False),
            'queued': runs.filter(status=Status.get_queued(), batch_run=False),
            'filtering': filter_by,
            'sort': sort_by,
            'has_variables': bool(current_variables),
            'error_reason': error_reason,
        }

        if filter_by == 'experiment':
            experiments_and_runs = {}
            experiments = Experiment.objects.filter(reduction_runs__instrument=instrument_obj). \
                order_by('-reference_number').distinct()
            for experiment in experiments:
                associated_runs = runs.filter(experiment=experiment). \
                    order_by('-created')
                experiments_and_runs[experiment] = associated_runs
            context_dictionary['experiments'] = experiments_and_runs
        elif filter_by == 'batch_runs':
            runs = ReductionRun.objects.only('status', 'last_updated', 'run_version',
                                             'run_description').filter(instrument=instrument_obj, batch_run=True)
            max_items_per_page = request.GET.get('pagination', 10)
            custom_paginator = CustomPaginator(
                page_type=sort_by,
                query_set=runs.filter(batch_run=True),
                items_per_page=max_items_per_page,
                page_tolerance=3,
                current_page=request.GET.get('page', 1),
            )
            context_dictionary['paginator'] = custom_paginator
            context_dictionary['last_page_index'] = len(custom_paginator.page_list)
            context_dictionary['max_items'] = max_items_per_page
        else:
            max_items_per_page = request.GET.get('pagination', 10)
            custom_paginator = CustomPaginator(
                page_type=sort_by,
                query_set=runs,
                items_per_page=max_items_per_page,
                page_tolerance=3,
                current_page=request.GET.get('page', 1),
            )
            context_dictionary['paginator'] = custom_paginator
            context_dictionary['last_page_index'] = len(custom_paginator.page_list)
            context_dictionary['max_items'] = max_items_per_page

    except Exception:
        LOGGER.error(traceback.format_exc())
        return {'message': "An unexpected error has occurred when loading the instrument."}

    return context_dictionary
