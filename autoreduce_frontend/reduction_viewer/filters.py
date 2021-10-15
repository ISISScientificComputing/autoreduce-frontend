from autoreduce_db.reduction_viewer.models import ReductionRun
from django_filters.widgets import RangeWidget
from django_filters import FilterSet, DateFromToRangeFilter


class ReductionRunFilter(FilterSet):
    created = DateFromToRangeFilter(widget=RangeWidget(attrs={
        'type': 'date',
        'placeholder': 'dd-mm-yyyy',
        'label': 'created'
    }))

    class Meta:
        model = ReductionRun
        fields = ['run_number', 'instrument', 'run_description', 'created']

    def __init__(self, *args, **kwargs):
        super(ReductionRunFilter, self).__init__(*args, **kwargs)
        # doesn't push Submit button, QueryDict (in data) is empty so not all runs displayed at start
        if self.data == {}:
            self.queryset = self.queryset.none()
