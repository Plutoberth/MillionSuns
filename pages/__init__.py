__all__ = ("make_pages",)

import typing as t

from dash_models import Page
from .daily import daily_page
from .params import params_page
from .cost_graph import scenarios_page

if t.TYPE_CHECKING:
    from params import AllParams
    from dash import Dash


def make_pages(app: "Dash", model_params: "AllParams") -> t.Sequence[Page]:
    """
    Get all pages in the module using the given app.
    """
    return (
        params_page(app, model_params),
        scenarios_page(app, model_params),
        daily_page(app, model_params),
    )
