import typing as t

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

from dash_models import Page
from dash_models.utils import comp_id

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import AllParams
    from dash import Dash


def fake_costs_calc(params: "AllParams") -> pd.DataFrame:
    return pd.read_csv("scenario_costs.csv")


def scenarios_page(app: "Dash", params: "AllParams") -> Page:
    plot_div_id = comp_id("plot_div")
    update_btn = comp_id("update_btn")

    @app.callback(
        Output(plot_div_id, "figure"),
        Input(update_btn, "n_clicks"),
    )
    def calc(_n_clicks: int) -> "Figure":
        fig = px.bar(
            data_frame=fake_costs_calc(params),
            x="Renewable Energy Usage Percentage",
            y="Cost",
            color="Cost Source",
            barmode="stack",
            title="Scenarios Cost By Renewable Generation Percentage",
            # TODO these colors dont seem to be working
            color_discrete_map={
                "Fossil": "Grey",
                "Pollution": "LightGrey",
                "Wind": "Green",
                "Solar": "Yellow",
                "Storage": "DeepSkyBlue",
            },
        )

        # TODO add BAU for reference
        fig.add_hline(80)

        fig.update_traces(marker_line_width=1.5, opacity=0.7)

        return fig

    return Page(
        title="Scenario Distribution",
        layout=html.Div(
            [
                dbc.Button(id=update_btn, class_name="m-3", children="Update"),
                dcc.Graph(id=plot_div_id),
            ]
        ),
    )
