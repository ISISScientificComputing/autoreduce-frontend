# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Module for the search runs page model."""

from django.urls import reverse

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class SearchPage(Page, NavbarMixin, FooterMixin):
    @staticmethod
    def url_path():
        """
        Return the path section of the overview page url
        :return: (str) Path section of the page url
        """
        return reverse("search")

    def alert_message_text(self) -> str:
        """
        Return the text of the alert message element with the id
        'alert_message'.
        """
        return self.driver.find_element_by_id("message").text.strip()