import django_tables2 as tables
from django_tables2 import Column, Table
from autoreduce_db.reduction_viewer.models import ReductionRun


class ReductionRunTable(Table):
    run_number = tables.Column(attrs={"a": {
        "class": "run-num-links"
    }},
                               linkify=('runs:summary', {
                                   'instrument_name': tables.A('instrument'),
                                   'run_number': tables.A('run_number')
                               }))

    class Meta:
        model = ReductionRun
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'instrument',
            'created',
        )
        sequence = (
            'run_number',
            'instrument',
            'created',
        )
