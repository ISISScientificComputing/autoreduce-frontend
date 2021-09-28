from autoreduce_db.instrument.models import Variable
from django.http.request import QueryDict


def read_variables_from_form_post_submit(post_data: QueryDict) -> dict:
    """Process the variables submitted in the request's POST data
    and return a dictionary containing the standard and advanced variables

    :param post_data: The request's POST dictionary. It will be filtered for variables
    :return: Dictionary containign standard_vars and advanced_vars keys.
    """

    # [(startswith+name, value) or ("var-advanced-"+name, value)]
    var_list = [t for t in post_data.items() if t[0].startswith("var-")]

    def _decode_dict(var_list, startswith: str):
        return {
            Variable.decode_name_b64(var[0].replace(startswith, "")): var[1]
            for var in var_list if var[0].startswith(startswith)
        }

    standard_vars = _decode_dict(var_list, "var-standard-")
    advanced_vars = _decode_dict(var_list, "var-advanced-")
    return {"standard_vars": standard_vars, "advanced_vars": advanced_vars}
