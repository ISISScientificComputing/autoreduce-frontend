# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #


"""
Module containing the Page object classes
"""
from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from webtests import configuration
from webtests.pages.component_mixins.footer_mixin import FooterMixin
from webtests.pages.component_mixins.navbar_mixin import NavbarMixin
from webtests.pages.component_mixins.tour_mixin import TourMixin


class Page(ABC):
    """
    Abstract base class for page object model classes
    """

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    @abstractmethod
    def url_path():
        """
        Abstract method to return the path section of the page URL
        """

    @classmethod
    def url(cls):
        """
        Return the URL of the page object
        :return: (str) The url of the page object
        """
        return configuration.get_url() + cls.url_path()

    def launch(self):
        """
        Navigate the webdriver to this page
        :return: The page object
        """
        self.driver.get(self.url())
        return self


class OverviewPage(Page, NavbarMixin, FooterMixin, TourMixin):
    """
    Overview page model class
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.step = 0

    def launch(self):
        """
        This is a bit of a hack to get around the fact that you will only be logged in when
        connecting to / and not /overview Once we have a better way to simulate logging in on the
        dev/local environments we can remove this method and add proper logging in methods and tests
        """
        self.driver.get(configuration.get_url())
        self.driver.get(OverviewPage.url())
        WebDriverWait(self.driver, 10).until(
            presence_of_element_located((By.CLASS_NAME, "instrument-btn")))
        return self

    @staticmethod
    def url_path():
        """
        Return the path section of the overview page url
        :return: (str) Path section of the page url
        """
        return "/overview/"

    def _get_instrument_buttons(self):
        return self.driver.find_elements_by_class_name("instrument-btn")

    def get_instruments_from_buttons(self):
        """
        Gets the names of the instruments which have buttons on the overview page
        :return: (List) The instrument names which have buttons on the overview page
        """
        return [instrument_btn.get_attribute("id").split("-")[0] for instrument_btn in
                self._get_instrument_buttons()]

    def click_instrument(self, instrument):
        """
        Clicks the instrument button for the given instrument
        :param instrument: (str) instrument name
        :return:
        """
        self.driver.find_element_by_id(f"{instrument}-instrument-btn").click()
        return self  # Return instrument page


class HelpPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for help page
    """

    @staticmethod
    def url_path():
        """
        Return the path section of the help page
        :return: (str) Path section of the page url
        """
        return "/help/"


class InstrumentSummaryPage(Page, NavbarMixin, FooterMixin, TourMixin):
    """
    Page model class for instrument summary page
    """

    @staticmethod
    def url_path():
        """
        Return the path section of the instrument url
        :return: (str) Path section of the page url
        """
        return "/instrument/%s/"


class JobQueuePage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for job queue page
    """

    @staticmethod
    def url_path():
        """
        Return the path section of the job queue url
        :return: (str) Path section of the page url
        """
        return "/runs/queue/"


class FailedJobsPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for failed jobs page
    """

    @staticmethod
    def url_path():
        """
        Return the path section of the failed jobs url
        :return: (str) Path section of the page url
        """
        return "/runs/failed/"


class GraphsPage(Page):
    """
    Page model class for graphs page
    """

    @staticmethod
    def url_path():
        """
        Return the path section of the graphs url
        :return: (str) Path section of the page url
        """
        return "/graph/"
