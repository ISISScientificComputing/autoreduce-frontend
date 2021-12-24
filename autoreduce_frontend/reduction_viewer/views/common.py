# ############################################################################ #
# Autoreduction Repository :
# https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################ #
# pylint:disable=too-many-return-statements,broad-except
import base64
import itertools
import json
import os
from typing import Tuple
from logging import getLogger
import traceback

import requests

from autoreduce_db.reduction_viewer.models import ReductionArguments
from autoreduce_qp.queue_processor.variable_utils import VariableUtils

UNAUTHORIZED_MESSAGE = "User is not authorized to submit batch runs. Please contact the Autoreduce team "\
                       "at ISISREDUCE@stfc.ac.uk to request the permissions."
# Holds the default value used when there is no value for the variable
# in the default variables dictionary. Stored in a parameter for re-use in
# tests
DEFAULT_WHEN_NO_VALUE = ""

logger = getLogger(__package__)


def _combine_dicts(current: dict, default: dict):
    """
    Combine the current and default variable dictionaries, into a single
    dictionary which can be more easily rendered into the webapp.

    If no current variables are provided, return the default as both current and
    default.
    """
    if not current:
        current = default.copy()

    final = {}
    for name in itertools.chain(current.keys(), default.keys()):
        # The default value for argument, also used when the variable is missing
        # from the current variables ideally there will always be a default for
        # each variable name, but if the variable is missing from the default
        # dictionary, then just default to empty string
        default_value = default.get(name, DEFAULT_WHEN_NO_VALUE)
        final[name] = {"current": current.get(name, default_value), "default": default_value}

    return final


def unpack_arguments(arguments: dict) -> Tuple[dict, dict, dict]:
    """
    Unpacks an arguments dictionary into separate dictionaries for
    standard, advanced variables, and variable help.

    Args:
        arguments: The arguments dictionary to unpack.

    Returns:
        A tuple containing the standard variables, advanced variables, and
        variable help.
    """
    standard_arguments = arguments.get("standard_vars", {})
    advanced_arguments = arguments.get("advanced_vars", {})
    variable_help = arguments.get("variable_help", {"standard_vars": {}, "advanced_vars": {}})
    return standard_arguments, advanced_arguments, variable_help


def get_arguments_from_file(instrument: str) -> Tuple[dict, dict, dict]:
    """
    Loads the default variables from the instrument's reduce_vars file.

    Args:
        instrument: The instrument to load the variables for.

    Raises:
        FileNotFoundError: If the instrument's reduce_vars file is not found.
        ImportError: If the reduce_vars file contains an import error.
        SyntaxError: If the reduce_vars file contains a syntax error.
    """
    default_variables = VariableUtils.get_default_variables(instrument)
    default_standard_variables, default_advanced_variables, variable_help = unpack_arguments(default_variables)
    return default_standard_variables, default_advanced_variables, variable_help


def prepare_arguments_for_render(arguments: ReductionArguments, instrument: str) -> Tuple[dict, dict, dict]:
    """
    Converts the arguments into a dictionary containing their "current" and
    "default" values.

    Used to render the form in the webapp (with values from "current"), and
    provide the defaults for resetting (with values from "default").

    Args:
        arguments: The arguments to convert.
        instrument: The instrument to get the default variables for.

    Returns:
        A dictionary containing the arguments and their current and default
        values.
    """
    vars_kwargs = arguments.as_dict()

    standard_vars = vars_kwargs.get("standard_vars", {})
    advanced_vars = vars_kwargs.get("advanced_vars", {})

    default_standard_variables, default_advanced_variables, variable_help = get_arguments_from_file(instrument)

    final_standard = _combine_dicts(standard_vars, default_standard_variables)
    final_advanced = _combine_dicts(advanced_vars, default_advanced_variables)

    fetch_api_urls(final_standard)
    fetch_api_urls(final_advanced)

    return final_standard, final_advanced, variable_help


def fetch_api_urls(vars_kwargs):
    """Convert file URLs in vars_kwargs into API URL strings."""
    for _, heading_value in vars_kwargs.items():
        if isinstance(heading_value["current"], dict) and "url" in heading_value["current"]:
            try:
                heading_value["all_files"] = {}
                base_url, _, path = heading_value["current"]["url"].partition("master")
                # TODO might want to support >1 origin, or allow different syntax
                repo = base_url.replace("https://raw.githubusercontent.com/", "")[:-1]  # :-1 drops the trailing slash
                path = path.lstrip("/")
                url = f"https://api.github.com/repos/{repo}/contents/{path}"
                auth_token = os.environ.get("AUTOREDUCTION_GITHUB_AUTH_TOKEN", None)
                headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
                req = requests.get(url, headers=headers)
                data = json.loads(req.content)

                for link in data:
                    file_name = link["name"]
                    # if this download_url is None, then it's a directory
                    if link["download_url"]:
                        url, _, default = link["download_url"].rpartition("/")
                        heading_value["all_files"][file_name] = {
                            "url": url,
                            "default": default,
                        }
            except Exception as err:
                logger.error("Failed to fetch file from GitHub: %s\n%s", str(err), traceback.format_exc())


def decode_b64(value: str):
    """Decodes the base64 representation back to utf-8 string."""
    return base64.urlsafe_b64decode(value).decode("utf-8")


def convert_to_python_type(value: str):
    """
    Converts the string sent by the POST request to a real Python type that can
    be serialized by JSON.

    Args:
        value: The string value to convert.

    Returns:
        The converted value.
    """
    try:
        # JSON can directly load str/int/floats and lists of them
        return json.loads(value)
    except json.JSONDecodeError:
        lowered_value = value.lower()
        if lowered_value in ("none", "null"):
            return None
        if lowered_value == "true":
            return True
        if lowered_value == "false":
            return False
        if "," in value and "[" not in value and "]" not in value:
            return convert_to_python_type(f"[{value}]")
        if "'" in value:
            return convert_to_python_type(value.replace("'", '"'))

        return value


def make_reduction_arguments(post_arguments: dict, instrument: str) -> dict:
    """
    Given new variables from the POST request and the default variables from
    reduce_vars.py create a dictionary of the new variables

    Args:
        post_arguments: The new variables to be created.
        default_variables: The default variables.

    Returns:
        The new variables as a dict.

    Raises:
        ValueError: If any variable values exceed the allowed maximum.
    """

    defaults = VariableUtils.get_default_variables(instrument)

    for key, value in post_arguments:
        if 'var-' in key:
            if 'var-advanced-' in key:
                name = key.replace('var-advanced-', '')
                dict_key = "advanced_vars"
            elif 'var-standard-' in key:
                name = key.replace('var-standard-', '')
                dict_key = "standard_vars"
            else:
                continue

            if name is not None:
                name = decode_b64(name)
                # Skips variables that have been removed from the defaults
                if name not in defaults[dict_key]:
                    continue

                defaults[dict_key][name] = convert_to_python_type(value)

    return defaults
