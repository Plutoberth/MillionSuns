import typing as t

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

from dash_models import Page
from dash_models.utils import comp_id
from data.reader import get_filename

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import AllParams
    from dash import Dash

from common import ScenarioCostFields

# Business-as-usual pricing
BAU = 55.365095440

COLOR_MAP = {
    "Fossil": "Grey",
    "Pollution": "LightGrey",
    "Wind": "Green",
    "Solar": "Yellow",
    "Storage": "DeepSkyBlue",
}


def calc_costs(params: "AllParams") -> pd.DataFrame:
    return pd.read_csv(get_filename("fake_costs.csv"))


def scenarios_page(app: "Dash", params: "AllParams") -> Page:
    plot_div_id = comp_id("plot_div")
    update_btn = comp_id("update_btn")

    @app.callback(
        Output(plot_div_id, "figure"),
        Input(update_btn, "n_clicks"),
    )
    def calc(_) -> "Figure":
        df = calc_costs(params)
        bau = BAU

        usage_pct = ScenarioCostFields.RENEWABLE_ENERGY_USAGE_PERCENTAGE.value
        cost = ScenarioCostFields.COST.value
        cost_source = ScenarioCostFields.COST_SOURCE.value

        # Creates figure object and adds bar graph to it
        fig = px.bar(
            data_frame=df,
            x=usage_pct,
            y=cost,
            color=cost_source,
            barmode="stack",
            title="Scenario Costs",
            color_discrete_map=COLOR_MAP,
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
            y=1.05 * bau,
            showarrow=False,
            text="Business As Usual: {} Billion ILS".format(bau),
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
