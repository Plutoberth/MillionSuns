import typing as t

from dash_models import Page

if t.TYPE_CHECKING:
    from params import AllParams
    from dash import Dash


def params_page(app: "Dash", params: "AllParams") -> Page:
    return Page(
        title="Parameters",
        layout=params.dash_editor(
            app,
            "Params",
            "Enter ranges of interpolated predictions,"
            " which will be combined with 2018 data,"
            " to simulate energy production and usage in the future.",
        ),
    )
