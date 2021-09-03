from django.views.generic import TemplateView
from autoreduce_db.instrument.models import Instrument


class BatchRunSummary(TemplateView):
    template_name = 'batch_run.html'

    def get_context_data(self, **kwargs):
        instrument = Instrument.objects.get(name=kwargs.get('instrument_name'))

        context = super(BatchRunSummary, self).get_context_data(**kwargs)
        context['instrument'] = instrument
        context['standard_variables'] = final_standard
        context['advanced_variables'] = final_advanced
        return context
