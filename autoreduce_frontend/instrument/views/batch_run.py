import requests
import json
from autoreduce_frontend.utilities import input_processing
from autoreduce_frontend.instrument.views.common import read_variables_from_form_post_submit
from typing import Any
from autoreduce_qp.queue_processor.reduction.service import ReductionScript
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import TemplateView, FormView
from autoreduce_db.instrument.models import Instrument
from autoreduce_frontend.instrument.views.variables import _combine_dicts
from autoreduce_frontend.reduction_viewer.utils import ReductionRunUtils
from autoreduce_qp.queue_processor.variable_utils import VariableUtils
from autoreduce_qp.queue_processor.instrument_variable_utils import InstrumentVariablesUtils
from django.shortcuts import render
from autoreduce_utils.settings import AUTOREDUCE_API_URL


class BatchRun(TemplateView):
    template_name = 'batch_run.html'

    def get_context_data(self, **kwargs):
        context = super(BatchRun, self).get_context_data(**kwargs)
        instrument = Instrument.objects.prefetch_related('reduction_runs').get(name=kwargs.get('instrument'))

        # pylint:disable=no-member
        runs_for_instrument = instrument.reduction_runs.filter(batch_run=True)
        last_run = instrument.get_last_for_rerun(runs_for_instrument)

        kwargs = ReductionRunUtils.make_kwargs_from_runvariables(last_run)
        standard_vars = kwargs["standard_vars"]
        advanced_vars = kwargs["advanced_vars"]

        try:
            default_variables = VariableUtils.get_default_variables(instrument)
        except (FileNotFoundError, ImportError, SyntaxError) as err:
            return {"message": str(err)}

        final_standard = _combine_dicts(standard_vars, default_variables["standard_vars"])
        final_advanced = _combine_dicts(advanced_vars, default_variables["advanced_vars"])
        context['message'] = self.request.GET.get("error", None)
        context['instrument'] = instrument
        context['standard_variables'] = final_standard
        context['advanced_variables'] = final_advanced
        return context


class BatchRunSubmit(FormView):
    template_name = 'batch_run.html'

    def get_context_data(self, **kwargs):
        instrument = Instrument.objects.prefetch_related('reduction_runs').get(name=kwargs.get('instrument'))

        # pylint:disable=no-member
        runs_for_instrument = instrument.reduction_runs.filter(batch_run=True)
        last_run = instrument.get_last_for_rerun(runs_for_instrument)

        kwargs = ReductionRunUtils.make_kwargs_from_runvariables(last_run)
        standard_vars = kwargs["standard_vars"]
        advanced_vars = kwargs["advanced_vars"]

        try:
            default_variables = VariableUtils.get_default_variables(instrument)
        except (FileNotFoundError, ImportError, SyntaxError) as err:
            return {"message": str(err)}

        final_standard = _combine_dicts(standard_vars, default_variables["standard_vars"])
        final_advanced = _combine_dicts(advanced_vars, default_variables["advanced_vars"])
        context = {}
        context['error'] = self.request.GET.get("error", None)
        context['instrument'] = instrument
        context['standard_variables'] = final_standard
        context['advanced_variables'] = final_advanced
        return context

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def render_error(self, request, message: str, runs, **kwargs):
        """Render the GET page but with an additional error message"""
        context = self.get_context_data(**kwargs)
        context["error"] = message
        context["runs"] = runs
        return render(request, self.template_name, context)

    def render_confirm(self, request, instrument: str, runs, kwargs):
        """Render the GET page but with an additional error message"""
        context = self.get_context_data(**kwargs)
        context["runs"] = runs
        context["instrument_name"] = instrument
        return render(request, "batch_run_confirmation.html", context)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        instrument_name = kwargs["instrument"]

        input_runs = request.POST.get("runs", None)
        if not input_runs:
            return self.render_error(request, "Run field was invalid or empty", input_runs, **kwargs)

        try:
            auth_token = str(request.user.auth_token)
        except AttributeError as err:
            return self.render_error(request, "User is not authorized to submit batch runs.", input_runs, **kwargs)
        runs = input_processing.parse_user_run_numbers(input_runs)
        all_vars = read_variables_from_form_post_submit(request.POST)

        reduce_vars = ReductionScript(instrument_name, 'reduce_vars.py')
        reduce_vars_module = reduce_vars.load()
        try:
            args_for_range = InstrumentVariablesUtils.merge_arguments(all_vars, reduce_vars_module)
        except KeyError as err:
            return self.render_error(
                request, f"Error encountered when processing variable with name: {err}. \
                 Please check that the names of the variables in reduce_vars.py match the \
                 names of the variables shown in the web app.", **kwargs)

        try:
            response = requests.post(f"{AUTOREDUCE_API_URL}/runs/batch/{kwargs['instrument']}",
                                     json={
                                         "runs": runs,
                                         "reduction_arguments": args_for_range
                                     },
                                     headers={"Authorization": f"Token {auth_token}"})
            if response.status_code != 200:
                content = json.loads(response.content)
                return self.render_error(request, content.get("message", "Unknown error encountered"), input_runs,
                                         **kwargs)
        except Exception as err:
            return self.render_error(request, input_runs, str(err), **kwargs)
        return self.render_confirm(request, instrument_name, runs, kwargs)
