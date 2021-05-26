from unittest.mock import Mock, patch

from autoreduce_frontend.reduction_viewer import views
from autoreduce_frontend.autoreduce_webapp.icat_cache import DEFAULT_MESSAGE
from autoreduce_frontend.autoreduce_webapp.view_utils import ICATConnectionException
from autoreduce_frontend.selenium_tests.pages.error_page import ErrorPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (BaseTestCase, FooterTestMixin, NavbarTestMixin)


class TestErrorPage(NavbarTestMixin, BaseTestCase, FooterTestMixin):
    """
    Test cases for the error page
    """
    fixtures = BaseTestCase.fixtures + ["test_overview_page"]

    def setUp(self) -> None:
        """
        Sets up the ErrorPage object
        """
        super().setUp()
        self.page = ErrorPage(self.driver)

    @patch('autoreduce_webapp.reduction_viewer.views.authenticate', side_effect=ICATConnectionException)
    def test_error_message(self, authenticate: Mock):
        """
        Test that the page error message matches the expected error

        This turns off development mode - this will attempt to use UOWS authentication
        but it's mocked out to raise the ICATConnectionException, so we test the error path.

        At the end it turns it back on or following tests will fail
        """
        views.DEVELOPMENT_MODE = False
        self.page.launch_with_session()
        self.assertEqual(DEFAULT_MESSAGE, self.page.get_error_message())
        authenticate.assert_called_once_with(token=self.page.fake_token)
        views.DEVELOPMENT_MODE = True
