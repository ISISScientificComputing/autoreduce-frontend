import base64
import itertools
from typing import Tuple
from autoreduce_db.reduction_viewer.models import ReductionArguments
from autoreduce_qp.queue_processor.variable_utils import VariableUtils
from django.http.request import QueryDict


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
        # the default value for argument, also used when the variable is missing from the current variables
        # ideally there will always be a default for each variable name, but
        # if the variable is missing from the default dictionary, then just default to empty string
        default_value = default.get(name, "")
        final[name] = {"current": current.get(name, default_value), "default": default_value}

    return final


def unpack_arguments(arguments: dict) -> Tuple[dict, dict, dict]:
    """
    Unpacks an arguments dictionary into separate dictionaries for
    standard, advanced variables, and variable help.

    Args:
        arguments: The arguments dictionary to unpack.

    Returns:
        A tuple containing the standard variables, advanced variables, and variable help.
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
        ImportError: If the instrument's reduce_vars file contains an import error.
        SyntaxError: If the instrument's reduce_vars file contains a syntax error.
    """
    try:
        default_variables = VariableUtils.get_default_variables(instrument)
        default_standard_variables, default_advanced_variables, variable_help = unpack_arguments(default_variables)
    except (FileNotFoundError, ImportError, SyntaxError):
        default_standard_variables = {}
        default_advanced_variables = {}
        variable_help = {"standard_vars": {}, "advanced_vars": {}}
    return default_standard_variables, default_advanced_variables, variable_help


def prepare_arguments_for_render(arguments: ReductionArguments, instrument: str) -> Tuple[dict, dict, dict]:
    """
    Converts the arguments into a dictionary containing their "current" and "default" values.

    Used to render the form in the webapp (with values from "current"), and
    provide the defaults for resetting (with values from "default").

    Args:
        arguments: The arguments to convert.
        instrument: The instrument to get the default variables for.

    Returns:
        A dictionary containing the arguments and their current and default values.
    """
    vars_kwargs = arguments.as_dict()
    standard_vars = vars_kwargs.get("standard_vars", {})
    advanced_vars = vars_kwargs.get("advanced_vars", {})

    default_standard_variables, default_advanced_variables, variable_help = get_arguments_from_file(instrument)

    final_standard = _combine_dicts(standard_vars, default_standard_variables)
    final_advanced = _combine_dicts(advanced_vars, default_advanced_variables)

    return final_standard, final_advanced, variable_help


def decode_b64(value: str):
    """
    Decodes the base64 representation back to utf-8 string.
    """
    return base64.urlsafe_b64decode(value).decode("utf-8")


def read_variables_from_form_post_submit(post_data: QueryDict) -> dict:
    """Process the variables submitted in the request's POST data
    and return a dictionary containing the standard and advanced variables

    :param post_data: The request's POST dictionary. It will be filtered for variables
    :return: Dictionary containign standard_vars and advanced_vars keys.
    """

    # [(startswith+name, value) or ("var-advanced-"+name, value)]
    var_list = [t for t in post_data.items() if t[0].startswith("var-")]

    def _decode_dict(var_list, startswith: str):
        return {decode_b64(var[0].replace(startswith, "")): var[1] for var in var_list if var[0].startswith(startswith)}

    standard_vars = _decode_dict(var_list, "var-standard-")
    advanced_vars = _decode_dict(var_list, "var-advanced-")
    return {"standard_vars": standard_vars, "advanced_vars": advanced_vars}
