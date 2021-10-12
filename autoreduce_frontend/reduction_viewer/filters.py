from autoreduce_db.reduction_viewer.models import ReductionRun
import django_filters


class ReductionRunFilter(django_filters.FilterSet):
    class Meta:
        model = ReductionRun
        fields = [
            'run_number',
            'instrument',
            'run_description',
            'last_updated',
        ]

    def __init__(self, *args, **kwargs):
        super(ReductionRunFilter, self).__init__(*args, **kwargs)
        # at sturtup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()
