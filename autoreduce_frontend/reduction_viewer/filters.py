from autoreduce_db.reduction_viewer.models import ReductionRun
from django_filters.filters import Filter
from django_filters.widgets import RangeWidget
from django_filters import FilterSet, DateFromToRangeFilter


class RunNumberField(Filter):
    """ This is a custom FilterField to enable a behavior like:
        ?run_number=1,2,3,4 ... 
        """
    def filter(self, queryset, value):

        # If no value is passed, return initial queryset
        if not value:
            return queryset

        self.lookup_expr = 'in'  # Setting the lookupexpression for all values
        list_values = value.split(',')  # Split the incoming querystring by comma

        return super(RunNumberField, self).filter(queryset, list_values)


class ReductionRunFilter(FilterSet):
    created = DateFromToRangeFilter(widget=RangeWidget(attrs={
        'type': 'date',
        'placeholder': 'dd-mm-yyyy',
        'label': 'created'
    }))

    run_number = RunNumberField(field_name='run_number')

    class Meta:
        model = ReductionRun
        fields = ['run_number', 'instrument', 'run_description', 'created']

    def __init__(self, *args, **kwargs):
        super(ReductionRunFilter, self).__init__(*args, **kwargs)
        # doesn't push Submit button, QueryDict (in data) is empty so not all runs displayed at start
        if self.data == {}:
            self.queryset = self.queryset.none()
