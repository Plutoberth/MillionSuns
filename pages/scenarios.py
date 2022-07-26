import typing as t

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, dcc, html

from dash_models import Page
from dash_models.utils import comp_id

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import Params
    from dash import Dash


def scenarios_page(app: "Dash", params: "Params") -> Page:
    plot_div_id = comp_id("plot_div")
    update_btn = comp_id("update_btn")

    @app.callback(
        Output(plot_div_id, "figure"),
        Input(update_btn, "n_clicks"),
        prevent_initial_callback=True,
    )
    def calc(day: int) -> "Figure":
        # TODO actual calculation

        return px.bar(
            px.data.gapminder().query("country == 'Canada'"), x="year", y="pop"
        )

    return Page(
        title="Scenario Distribution",
        layout=html.Div(
            [
                dbc.Button(id=update_btn, class_name="m-3", children="Update"),
                dcc.Graph(id=plot_div_id),
            ]
        ),
    )
