# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the error page model
"""
from django.urls.base import reverse

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class FailedJobsPage(Page, NavbarMixin, FooterMixin):
    @staticmethod
    def url_path() -> str:
        """
        This needs to be overriden because the basemethod is abstract, but it isn't used
        because the launch method is overriden here too.

        :return: (str) the url path
        """
        return reverse("runs:failed")

    def get_failed_runs(self) -> list:
        """
        Gets the failed runs from the page

        :return: (list) a list of failed run objects
        """
        return self.driver.find_elements_by_class_name("failed-run-link")
