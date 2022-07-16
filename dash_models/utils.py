from secrets import token_hex


def comp_id(s: str) -> str:
    return f'dash_models__{s}__{token_hex(8)}'
