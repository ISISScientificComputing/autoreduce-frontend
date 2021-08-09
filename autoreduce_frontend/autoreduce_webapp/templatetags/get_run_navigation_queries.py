# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from django.template import Library

register = Library()


@register.simple_tag
def get_run_navigation_queries(run_number: str, page: int, newest_run: int, oldest_run: int) -> str:
    """Return a string of run queries."""
    run_number = int(run_number)
    return (f"page={page}&newest_run={newest_run}&next_run={run_number+1}&"
            f"previous_run={run_number-1}&oldest_run={oldest_run}")
