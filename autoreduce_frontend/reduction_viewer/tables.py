import django_tables2 as tables
from django_tables2 import Table
from autoreduce_db.reduction_viewer.models import ReductionRun, Experiment
from autoreduce_frontend.autoreduce_webapp.templatetags.colour_table_row import colour_table_row


class ReductionRunTable(Table):
    def data_status(**kwargs):
        status = kwargs.get("value", None)
        if status is None:
            return "header"
        else:
            return "text-" + colour_table_row(status.__str__()) + " run-status"

    run_number = tables.TemplateColumn(
        '{% load generate_run_link %} <a href="{% generate_run_link instrument_name record current_page last_instrument_run first_instrument_run %}&per_page={{ per_page }}&sort={{ sort }}&filter={{ filtering }}">{{record.run_number}}</a>',
        attrs={"td": {
            "class": "run-num-links"
        }},
        accessor="run_numbers__run_number")

    status = tables.Column(attrs={"td": {"class": data_status}})

    created = tables.DateTimeColumn(attrs={"td": {"class": "created-dates"}})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ReductionRun
        row_attrs = {"class": "run-row"}
        fields = (
            'run_number',
            'instrument',
            'status',
            'created',
        )
        sequence = (
            'run_number',
            'instrument',
            'status',
            'created',
        )


class ReductionRunSearchTable(Table):
    def data_status(**kwargs):
        status = kwargs.get("value", None)
        if status is None:
            return "header"
        else:
            return "text-" + colour_table_row(status.__str__()) + " run-status"

    run_number = tables.TemplateColumn(
        '{% load get_run_navigation_queries %} <a href="{% url \'runs:summary\' record.instrument record.run_number record.run_version %}?page={{current_page}}&per_page={{per_page}}&sort={{ sort }}&filter={{ filtering }}">{{record.run_number}}</a>',
        attrs={"td": {
            "class": "run-num-links"
        }},
        accessor="run_numbers__run_number")

    status = tables.Column(attrs={"td": {"class": data_status}})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = ReductionRun
        row_attrs = {"class": "run-row"}
        fields = (
            'run_number',
            'instrument',
            'status',
            'created',
        )
        sequence = (
            'run_number',
            'instrument',
            'status',
            'created',
        )


class ExperimentTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    reference_number = tables.TemplateColumn(
        '<a href="{% url \'experiment_summary\' record.reference_number %}" onClick="event.stopPropagation();">RB{{ record.reference_number }}</a>',
        attrs={"td": {
            "class": "experiment-num-links"
        }})

    class Meta:
        model = Experiment
        row_attrs = {"class": "experiment-row", "data-target": "#RB{{ experiment.reference_number }}"}
        fields = ('reference_number', )
