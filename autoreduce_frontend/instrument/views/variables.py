# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
View functions for displaying Variable data. This imports into another view,
thus no middleware.
"""
# pylint:disable=too-many-locals,no-member,unused-argument
import logging

from django.shortcuts import redirect, render

from autoreduce_db.reduction_viewer.models import Instrument, ReductionArguments
from autoreduce_qp.queue_processor.variable_utils import VariableUtils
from autoreduce_frontend.autoreduce_webapp.view_utils import check_permissions, login_and_uows_valid, render_with

LOGGER = logging.getLogger(__package__)


def summarize_variables(request, instrument, last_run_object):
    """Handle view request for the instrument summary page."""
    instrument = Instrument.objects.get(name=instrument)

    current_arguments = last_run_object.arguments

    upcoming_arguments_by_run = ReductionArguments.objects.filter(start_run__gt=last_run_object.run_number,
                                                                  instrument=instrument)
    upcoming_arguments_by_experiment = ReductionArguments.objects.filter(
        experiment_reference__gte=last_run_object.experiment.reference_number, instrument=instrument)

    # There's a known issue with inaccurate display of tracks script:
    # https://github.com/ISISScientificComputing/autoreduce/issues/1187
    # creates a nested dictionary for by-run
    upcoming_arguments_by_run_dict = {}
    for arguments in upcoming_arguments_by_run:
        if arguments.start_run not in upcoming_arguments_by_run_dict:
            upcoming_arguments_by_run_dict[arguments.start_run] = {
                'run_start': arguments.start_run,
                'run_end': 0,  # We'll fill this in after
                'arguments': arguments.as_dict(),
                'instrument': instrument,
            }

    # Fill in the run end numbers
    run_end = 0
    for run_number in sorted(upcoming_arguments_by_run_dict.keys(), reverse=True):
        upcoming_arguments_by_run_dict[run_number]['run_end'] = run_end
        run_end = max(run_number - 1, 0)

    if current_arguments:
        current_start = current_arguments.start_run
        if current_start is None:
            current_start = 0
        next_run_starts = list(
            filter(lambda start: start > current_start, sorted(upcoming_arguments_by_run_dict.keys())))
        current_end = next_run_starts[0] - 1 if next_run_starts else 0

        current_vars = {
            'run_start': current_start,
            'run_end': current_end,
            'arguments': current_arguments.as_dict(),
            'instrument': instrument,
        }
    else:
        current_vars = {}

    # Move the upcoming vars into an ordered list
    upcoming_arguments_by_run_ordered = []
    for key in sorted(upcoming_arguments_by_run_dict):
        upcoming_arguments_by_run_ordered.append(upcoming_arguments_by_run_dict[key])

    # Create a nested dictionary for by-experiment
    upcoming_variables_by_experiment_dict = {}
    for arguments in upcoming_arguments_by_experiment:
        if arguments.experiment_reference not in upcoming_variables_by_experiment_dict:
            upcoming_variables_by_experiment_dict[arguments.experiment_reference] = {
                'experiment': arguments.experiment_reference,
                'arguments': arguments.as_dict(),
                'instrument': instrument,
            }

    # Move the upcoming vars into an ordered list
    upcoming_arguments_by_experiment_ordered = []
    for key in sorted(upcoming_variables_by_experiment_dict):
        upcoming_arguments_by_experiment_ordered.append(upcoming_variables_by_experiment_dict[key])
    sorted(upcoming_arguments_by_experiment_ordered, key=lambda r: r['experiment'])

    context_dictionary = {
        'instrument': instrument,
        'current_variables': current_vars,
        'upcoming_arguments_by_run': upcoming_arguments_by_run_ordered,
        'upcoming_arguments_by_experiment': upcoming_arguments_by_experiment_ordered,
    }

    return render(request, 'snippets/instrument_summary_variables.html', context_dictionary)


@login_and_uows_valid
@check_permissions
def delete_instrument_variables(request, instrument=None, start=0, end=0, experiment_reference=None):
    """
    Handle request for deleting instrument variables.

    Args:
        instrument: Name of the instrument for which variables are being
        deleted.

        start: Run from which variables are being deleted.

        end: Limit of how many variables get deleted, otherwise a delete would
        wipe ALL variables > start.

        experiment_reference: If provided - use the experiment reference to
        delete variables instead of start_run.
    """

    # We "save" an empty list to delete the previous variables.
    if experiment_reference is not None:
        ReductionArguments.objects.filter(instrument__name=instrument,
                                          experiment_reference=experiment_reference).delete()
    else:
        start_run_kwargs = {"start_run__gte": start}
        if end > 0:
            start_run_kwargs["start_run__lte"] = end
        ReductionArguments.objects.filter(instrument__name=instrument, **start_run_kwargs).delete()

    return redirect('instrument:variables_summary', instrument=instrument)


@login_and_uows_valid
@check_permissions
@render_with('variables_summary.html')
def instrument_variables_summary(request, instrument):
    """Handle request to view instrument variables."""
    instrument = Instrument.objects.get(name=instrument)
    context_dictionary = {'instrument': instrument, 'last_instrument_run': instrument.reduction_runs.last()}
    return context_dictionary


@login_and_uows_valid
@check_permissions
@render_with('snippets/variables/form.html')
def current_default_variables(request, instrument=None):
    """Handle request to view default variables."""

    try:
        current_variables = VariableUtils.get_default_variables(instrument)
    except (FileNotFoundError, ImportError, SyntaxError) as err:
        return {"message": str(err)}

    standard_vars = current_variables["standard_vars"]
    advanced_vars = current_variables["advanced_vars"]
    context_dictionary = {
        'instrument': instrument,
        'standard_variables': standard_vars,
        'advanced_variables': advanced_vars,
    }

    return context_dictionary


def render_run_variables(request, instrument_name, reduction_run):
    """
    Handles request to view the summary of a run
    """
    # pylint:disable=no-member
    vars_kwargs = reduction_run.arguments.as_dict()
    standard_vars = vars_kwargs["standard_vars"]
    advanced_vars = vars_kwargs["advanced_vars"]

    try:
        default_variables = VariableUtils.get_default_variables(instrument_name)
        default_standard_variables = default_variables["standard_vars"]
        default_advanced_variables = default_variables["advanced_vars"]
        variable_help = default_variables["variable_help"]
    except (FileNotFoundError, ImportError, SyntaxError):
        default_variables = {}
        default_standard_variables = {}
        default_advanced_variables = {}
        variable_help = {}

    final_standard = _combine_dicts(standard_vars, default_standard_variables)
    final_advanced = _combine_dicts(advanced_vars, default_advanced_variables)

    context_dictionary = {
        'run_number': ",".join(str(rn.run_number) for rn in reduction_run.run_numbers.all()),
        'run_version': reduction_run.run_version,
        'has_reduce_vars': bool(default_variables),
        'batch_run': reduction_run.batch_run,
        'standard_variables': final_standard,
        'advanced_variables': final_advanced,
        'variable_help': variable_help,
        'instrument': reduction_run.instrument,
    }
    return render(request, 'snippets/run_variables.html', context_dictionary)


def _combine_dicts(current: dict, default: dict):
    """
    Combine the current and default variable dictionaries, into a single
    dictionary which can be more easily rendered into the webapp.

    If no current variables are provided, return the default as both current and
    default.
    """
    if not current:
        current = default.copy()

    final = {}
    for name, var in current.items():
        final[name] = {"current": var, "default": default.get(name, None)}

    return final
