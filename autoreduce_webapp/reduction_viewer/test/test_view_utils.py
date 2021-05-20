from unittest.mock import Mock, mock_open, patch
from autoreduce_webapp.autoreduce_django.settings import DATA_ANALYSIS_BASE_URL
from autoreduce_webapp.reduction_viewer.view_utils import get_interactive_plot_data, make_data_analysis_url


def test_make_data_analysis_url_no_instrument_in_string():
    """Test running with a string that doesn't have /instrument/"""
    assert make_data_analysis_url("apples") == ""


def test_make_data_analysis_url_good_url():
    """Test with good string"""
    result = make_data_analysis_url("/instrument/TestInstrument/RBNumber/RB1234567/autoreduced")
    assert "TestInstrument/RBNumber/RB1234567/autoreduced" in result
    assert DATA_ANALYSIS_BASE_URL in result


def test_get_interactive_plot_data():
    """
    Test that get_interactive_plot_data will read only the json calls as expected
    """
    locations = ["location1.png", "location1.json", "location2.jpg", "location2.json"]
    mopen: Mock = mock_open()
    with patch("autoreduce_webapp.reduction_viewer.view_utils.open", mopen, create=True):
        get_interactive_plot_data(locations)
    mopen.assert_any_call(locations[1], 'r')
    mopen.assert_any_call(locations[3], 'r')
    assert mopen.call_count == 2
