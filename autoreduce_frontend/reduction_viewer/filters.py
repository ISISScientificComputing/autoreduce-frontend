from autoreduce_db.reduction_viewer.models import ReductionRun
from django.forms.widgets import DateInput
import django_filters
from django_filters.filters import DateFromToRangeFilter
from django_filters.widgets import RangeWidget


class ReductionRunFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={
        'type': 'date',
        'placeholder': 'dd-mm-yyyy'
    }))

    class Meta:
        model = ReductionRun
        fields = ['run_number', 'instrument', 'run_description']

    def __init__(self, *args, **kwargs):
        super(ReductionRunFilter, self).__init__(*args, **kwargs)
        # doesn't push Submit button, QueryDict (in data) is empty so not all runs displayed at start
        if self.data == {}:
            self.queryset = self.queryset.none()
