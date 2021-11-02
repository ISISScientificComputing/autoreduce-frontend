from autoreduce_db.reduction_viewer.models import ReductionRun
import pytest
from django.core.exceptions import ValidationError
from autoreduce_frontend.reduction_viewer.filters import validate_run_number, filter_run_number

allowed_queries = ['60200', '60200,60201', '60200-60202', '60190-60200, 60180-60185']
banned_queries = ['60200$', '60200,', '60200-', 'a']


def test_allowed_queries():
    """
    Test running filter with allowed queries.
    Assert no ValidationError exception is raised
    """
    try:
        for query in allowed_queries:
            validate_run_number(query)
    except ValidationError as exc:
        assert False, {exc}


def test_banned_queries():
    """
    Test running filter with banned queries.
    Assert ValidationError exception is raised
    """
    for query in banned_queries:
        with pytest.raises(ValidationError) as exc:
            validate_run_number(query)
