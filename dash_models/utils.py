from secrets import token_hex


def comp_id(s: str) -> str:
    """
    Generate a unique id for a component using `token_hex`.
    The point is to have different ids for different instances of some model.

    :param s: General id for the component, like 'download_button'.
    :return: A ~unique id.
    """
    return f'dash_models__{s}__{token_hex(8)}'
