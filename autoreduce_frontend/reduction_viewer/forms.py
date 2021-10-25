from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

ITEMS_PER_PAGE = (
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (100, '100'),
    (250, '250'),
    (500, '500'),
)


class SearchOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SearchOptionsForm, self).__init__(*args, **kwargs)

    pagination = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'id': "select_per_page",
                'title': "The number of reduction jobs that should be shown per page",
                'name': "per_page",
                'onchange': 'update_page()'
            }),
        choices=ITEMS_PER_PAGE,
    )

    helper = FormHelper()
    helper.layout = Layout('pagination')
