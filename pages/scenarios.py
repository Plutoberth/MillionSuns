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

from enums import ScenariosCostHeader

BAU = 55.365095440

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
        df = fake_costs_calc()
        bau = BAU

        # Creates figure object and adds bar graph to it
        fig = px.bar(
            data_frame=df,
            x=df.columns[ScenariosCostHeader.RENEWABLE_ENERGY_USAGE_PERCENTAGE],
            y=df.columns[ScenariosCostHeader.COST],
            color=df.columns[ScenariosCostHeader.COST_SOURCE],
            barmode="stack",
            title="Scenarios Cost Graph",
            color_discrete_map={
                "Fossil": "Grey",
                "Pollution": "LightGrey",
                "Wind": "Green",
                "Solar": "Yellow",
                "Storage": "DeepSkyBlue",
            },
        )

        # add a horizontal "target" line
        fig.add_shape(
            type="line",
            line_color="red",
            line_width=4,
            opacity=1,
            line_dash="dash",
            x0=0,
            x1=1,
            xref="paper",
            y0=bau,
            y1=bau,
            yref="y",
        )

        # Add text to BAU line
        fig.add_annotation(
            xref="paper",
            yref="y",
            x=0.5,
            y= 1.05 * bau,
            showarrow=False,
            text="Bussiness As Usual Cost: {} Billion NIS".format(bau),
            font=dict(size=16, color="black"),
        )

        # Cosmetics
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
