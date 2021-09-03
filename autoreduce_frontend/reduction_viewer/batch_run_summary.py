from django.views.generic import TemplateView
from autoreduce_db.instrument.models import Instrument
from autoreduce_frontend.instrument.views.variables import _combine_dicts
from autoreduce_frontend.reduction_viewer.utils import ReductionRunUtils
from autoreduce_qp.queue_processor.variable_utils import VariableUtils


class BatchRunSummary(TemplateView):
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
        context = super(BatchRun, self).get_context_data(**kwargs)
        context['instrument'] = instrument
        context['standard_variables'] = final_standard
        context['advanced_variables'] = final_advanced
        return context
