from autoreduce_frontend.selenium_tests.pages.failed_jobs_page import FailedJobsPage
from unittest.mock import Mock, patch

from autoreduce_frontend.reduction_viewer import views
from autoreduce_frontend.autoreduce_webapp.icat_cache import DEFAULT_MESSAGE
from autoreduce_frontend.selenium_tests.tests.base_tests import (BaseTestCase, FooterTestMixin, NavbarTestMixin)


class TestJailedJobs(BaseTestCase):
    # class TestJailedJobs(NavbarTestMixin, BaseTestCase, FooterTestMixin):
    """
    Test cases for the error page
    """
    fixtures = BaseTestCase.fixtures + ["two_runs_failed"]

    def setUp(self) -> None:
        """
        Sets up the ErrorPage object
        """
        super().setUp()
        self.page = FailedJobsPage(self.driver)
        self.page.launch()

    def test_failed_runs_visible(self):
        """
        Test that the page error message matches the expected error

        This turns off development mode - this will attempt to use UOWS authentication
        but it's mocked out to raise the ICATConnectionException, so we test the error path.

        At the end it turns it back on or following tests will fail
        """
        assert len(self.page.get_failed_runs()) == 2
