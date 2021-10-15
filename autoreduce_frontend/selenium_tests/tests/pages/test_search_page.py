# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the search runs page."""

from autoreduce_frontend.selenium_tests.pages.search_page import SearchPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (
    NavbarTestMixin,
    BaseTestCase,
    FooterTestMixin,
)


class TestSearchPage(NavbarTestMixin, BaseTestCase, FooterTestMixin):
    """Test cases for the search runs page."""

    fixtures = BaseTestCase.fixtures

    def setUp(self) -> None:
        """
        Sets up the HelpPage object
        """
        super().setUp()
        self.page = SearchPage(self.driver)
        self.page.launch()

    def test_alert_message_when_no_results(self):
        """
        Test that the correct message is shown when there are no results for the search
        """
        self.page.launch()
        expected = "Sorry, no runs found for this criteria."
        assert self.page.alert_message_text() == expected