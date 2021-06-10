from autoreduce_frontend.instrument.views.variables import _combine_dicts


def test_combine_dicts_empty_current():
    """
    Test: The default is properly used as both "current" and "default"
    When: `current` is empty
    """
    default_test = {"test_var": 123}
    expected = {"test_var": {"current": 123, "default": 123}}
    assert _combine_dicts({}, default_test) == expected


def test_combine_dicts():
    """
    Test: combine dicts works as expected - returns a dict with current and default
    When: dicts with matching variables are passed in
    """
    current_test = {"test_var": 123}
    default_test = {"test_var": 654}
    expected = {"test_var": {"current": 123, "default": 654}}
    assert _combine_dicts(current_test, default_test) == expected


def test_combine_dicts_current_more_vars():
    """
    Test: Value is None when current variables has a variable that's not in the defaults
    When: the current_variables dict has a variable that is not matching
    """
    current_test = {"test_var": 123, "not_in_defaults": "test"}
    default_test = {"test_var": 123}
    expected = {"test_var": {"current": 123, "default": 123}, "not_in_defaults": {"current": "test", "default": None}}
    assert _combine_dicts(current_test, default_test) == expected
