import re
from autoreduce_db.reduction_viewer.models import Experiment, ReductionRun
from django_filters.filters import CharFilter
from django_filters.widgets import RangeWidget
from django_filters import FilterSet, DateFromToRangeFilter
from django.db.models import Q
from django.core.exceptions import ValidationError


def validate_run_number(self):
    if "," in self and "-" not in self:
        if not re.match(r'\d+,\d+', self):
            raise ValidationError("There must be a run number before and after the comma.")
    elif "-" in self and "," not in self:
        if not re.match(r'\d+-\d+', self):
            raise ValidationError("There must be a run number before and after the hyphen.")
    elif "-" and "," in self:
        if not re.match(r'\d+-\d+', self):
            raise ValidationError("There must be a run number before and after the hyphen.")
    else:
        if not re.match(r'^\d+$', self):
            raise ValidationError("Run number must be numeric.")


    # pylint:disable=unused-argument
def filter_run_number(queryset, name, value):
    # If no value is passed, return initial queryset
    if not value:
        return queryset
    if "," in value and "-" not in value:
        list_values = value.split(',')
        query = Q(run_numbers__run_number__in=list_values)
        return queryset.filter(query)
    if "-" in value and "," not in value:
        list_values = value.split('-')
        query = Q(run_numbers__run_number__range=(list_values[0], list_values[1]))
        return queryset.filter(query)
    if "-" and "," in value:
        query = Q()
        list_values = value.split(',')
        for pair in list_values:
            seperated_pair = pair.split('-')
            query.add(Q(run_numbers__run_number__range=(seperated_pair[0], seperated_pair[1])), Q.OR)
        return queryset.filter(query)
    query = Q(run_numbers__run_number__exact=value)
    return queryset.filter(query)


class ReductionRunFilter(FilterSet):

    created = DateFromToRangeFilter(widget=RangeWidget(attrs={
        'type': 'date',
        'placeholder': 'dd-mm-yyyy',
        'label': 'created'
    }))

    run_description = CharFilter(method="filter_run_description")
    run_number = CharFilter(field_name="run_number",
                            method=filter_run_number,
                            label='Run Number',
                            validators=[validate_run_number])

    class Meta:
        model = ReductionRun
        fields = ['run_number', 'instrument', 'run_description', 'created', 'status']

    def __init__(self, *args, run_description_qualifier=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Call empty qs here to prevent all runs showing when search page first loaded
        if self.data == {}:
            self.queryset = self.queryset.none()
        self.run_description_qualifier = run_description_qualifier

    def filter_run_description(self, queryset, name, value):
        if not value:
            return queryset
        checkbox = self.run_description_qualifier
        if checkbox == "exact":
            query = Q(run_description__exact=value)
            return queryset.filter(query)
        if checkbox == "contains":
            query = Q(run_description__contains=value)
            return queryset.filter(query)
        query = Q(run_description__exact=value)
        return queryset.filter(query)


class ExperimentFilter(FilterSet):
    class Meta:
        model = Experiment
        fields = ['reference_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Call empty qs here to prevent all runs showing when search page first loaded
        if self.data == {}:
            self.queryset = self.queryset.none()
