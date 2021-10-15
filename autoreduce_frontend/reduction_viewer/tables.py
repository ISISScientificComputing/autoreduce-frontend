import django_tables2 as tables
from django_tables2 import Table
from autoreduce_db.reduction_viewer.models import ReductionRun
import itertools


class ReductionRunTable(Table):

    run_number = tables.TemplateColumn(
        '<a href="{% url \'runs:summary\' record.instrument record.run_number record.run_version %}?page={{current_page}}&per_page={{per_page}}&sort={{ sort }}&filter={{ filtering }}">{{record.run_number}}</a>',
        attrs={"td": {
            "class": "run-num-links"
        }})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count()

    class Meta:
        model = ReductionRun
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'run_number',
            'instrument',
            'created',
        )
        sequence = (
            'run_number',
            'instrument',
            'created',
        )
