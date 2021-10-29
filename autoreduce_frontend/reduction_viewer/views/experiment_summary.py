import logging

from autoreduce_db.reduction_viewer.models import Experiment, ReductionRun
from autoreduce_frontend.autoreduce_webapp.icat_cache import ICATCache
from autoreduce_frontend.autoreduce_webapp.settings import DEVELOPMENT_MODE
from autoreduce_frontend.autoreduce_webapp.view_utils import check_permissions, login_and_uows_valid, render_with
from autoreduce_frontend.reduction_viewer.view_utils import started_by_id_to_name
from autoreduce_frontend.utilities.pagination import CustomPaginator

LOGGER = logging.getLogger(__package__)


@login_and_uows_valid
@check_permissions
@render_with('experiment_summary.html')
# pylint:disable=no-member,too-many-locals,broad-except
def experiment_summary(request, reference_number=None):
    """Render experiment summary."""
    try:
        experiment = Experiment.objects.get(reference_number=reference_number)
        runs = ReductionRun.objects.filter(experiment=experiment, batch_run=False).order_by('-last_updated')
        page = request.GET.get('page', 1)
        if page == '':
            page = 1
        max_items_per_page = request.GET.get('per_page', 10)
        custom_paginator = CustomPaginator(page_type='run',
                                           query_set=runs,
                                           items_per_page=max_items_per_page,
                                           page_tolerance=3,
                                           current_page=page)

        started_by = [started_by_id_to_name(run.started_by) for run in custom_paginator.current_page.records]
        runs_with_started_by = zip(custom_paginator.current_page.records, started_by)

        try:
            if DEVELOPMENT_MODE:
                # If we are in development mode use user/password for ICAT from
                # django settings e.g. do not attempt to use same authentication
                # as the user office
                with ICATCache() as icat:
                    experiment_details = icat.get_experiment_details(int(reference_number))
            else:
                with ICATCache(AUTH='uows', SESSION={'sessionid': request.session['sessionid']}) as icat:
                    experiment_details = icat.get_experiment_details(int(reference_number))

        except Exception as icat_e:
            LOGGER.error(icat_e)
            experiment_details = {
                'reference_number': '',
                'start_date': '',
                'end_date': '',
                'title': '',
                'summary': '',
                'instrument': '',
                'pi': '',
            }

        context_dictionary = {
            'experiment': experiment,
            'runs_with_started_by': runs_with_started_by,
            'run_count': len(runs),
            'experiment_details': experiment_details,
            'paginator': custom_paginator,
            'last_page_index': len(custom_paginator.page_list),
        }

    except Exception as exception:
        LOGGER.error(exception)
        context_dictionary = {"error": str(exception)}

    return context_dictionary
