from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.forms.fields import ChoiceField

FILTER_BY = (('run', 'Run number'), ('experiment', 'Experiment Reference (RB)'))

SORT_BY = (('run', 'Number'), ('date', 'Date'))

ITEMS_PER_PAGE = (
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (100, '100'),
    (250, '250'),
    (500, '500'),
)


class RunsListForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RunsListForm, self).__init__(*args, **kwargs)

    filter = forms.ChoiceField(choices=FILTER_BY, initial="run")
    sort = forms.ChoiceField(choices=SORT_BY, initial="run")
    pagination = forms.ChoiceField(choices=ITEMS_PER_PAGE, initial=10)

    helper = FormHelper()
    helper.form_class = 'form-inline'
    helper.layout = Layout('filter', 'sort', 'pagination')
    helper.field_template = 'bootstrap3/layout/inline_field.html'
