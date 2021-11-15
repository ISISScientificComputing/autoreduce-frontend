# ############################################################################ #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################ #
# pylint:disable=invalid-name
"""Handles colouring table rows."""
from django.template import Library

register = Library()

_STATUSES = {
    "Error": "danger",
    "Processing": "warning",
    "Queued": "info",
    "Completed": "success",
    "Skipped": "dark",
}


@register.simple_tag
def colour_table_row(status):
    """Switch statement for defining table colouring."""
    return _STATUSES.get(status, status)
