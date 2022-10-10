import math
import typing as t

import datetime
from dataclasses import dataclass

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, ctx, dcc, html

from dash_models import Page
from dash_models.utils import comp_id
from pages.graph_utils import month_marks, year_marks

from params.roadmap import Roadmap, RoadmapParam
from common import EnergySource, SimOutFields, SimUsageFields
from scenario_evaluator.run_scenarios import run_scenario
import functools

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import AllParams
    from dash import Dash

sim_results: list[pd.DataFrame] | None = None
SPAN = "</span>"
BR = "<br>"
ONLY_SOLAR = "onlysolar"
TICK_STEP = 20000
DAYS_IN_YEAR = 365

theta = [f"{n}:00" for n in range(24)]
no_fill_theta = list(theta)
no_fill_theta.append(theta[0])
width = [1] * 24


@dataclass
class BarField:
    name: str
    label: str
    color: str


def polar_bar(df: pd.DataFrame, day: int, field: BarField):
    r = df[field.name][(day * 24): (day + 1) * 24]
    return go.Barpolar(
        name=field.label,
        r=r,
        theta=theta,
        width=width,
        marker_color=field.color,
        hovertemplate="<i>%{theta} : %{r:,.0f} KW</i>",
    )


def polar_scatter(df: pd.DataFrame, day: int, name: str, label: str, color: str, fill=True, dash=False):
    r = df[name][(day * 24): (day + 1) * 24]
    if not fill:  # if fill is false then add another point to close the loop
        r = list(r)
        r.append(r[0])
    return go.Scatterpolar(
        name=label,
        r=r,
        theta=theta if fill else no_fill_theta,
        fillcolor=color,
        fill="toself" if fill else "none",
        marker=dict(color=color),
        line=dict(
            color=color,
            shape="spline",
            smoothing=0,
            dash=("dash" if dash else "solid"),
        ),
        hoveron="points",
        hovertemplate="<i>%{theta} : %{r:,.0f} KW</i>",
    )


def date_str(year: int, day_of_year: int):
    date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year)
    return date.strftime("%d %B, %Y")


def annotation(df: pd.DataFrame, year: int, day_of_year: int):
    df_by_date = df.groupby(["date"]).sum()

    date = date_str(year, day_of_year)
    total_demand_mwh = df_by_date[SimOutFields.DEMAND][day_of_year] / 1000
    solar_gen_mwh = df_by_date[ONLY_SOLAR][day_of_year] / 1000

    return (
            "<span style='font-weight:bolder;color:black;font-size: 20px'>"
            + date
            + SPAN
            + BR
            + BR
            + "<span style='color:red';font-size: 16px>Total Demand: {:.2f} "
              "MWh".format(total_demand_mwh)
            + SPAN
            + BR
            + "<span style='color:orange;font-size: 16px'>Solar Power: {:.2f} "
              "MWh".format(solar_gen_mwh) + SPAN + BR
    )


def barplot(df: pd.DataFrame, fields: list[BarField], year: int, day_of_year: int):
    f = go.Figure()

    for field in fields:
        f.add_trace(polar_bar(df, day_of_year, field))

    f.add_trace(polar_scatter(df, day_of_year, SimOutFields.DEMAND, "Demand", "red", False))
    f.add_trace(
        polar_scatter(df, day_of_year, SimOutFields.NET_DEMAND, "Net Demand", "purple", False, True)
    )
    f.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        text=annotation(df, year, day_of_year),
        font=dict(family="Arial", size=16, color="black"),
    )
    return f


def plot(df: pd.DataFrame, year: int, day_of_year: int):
    fields = [
        BarField(SimUsageFields.COAL, "Coal", "black"),
        BarField(SimUsageFields.GAS, "Gas", "lightgray"),
        BarField(SimUsageFields.WIND, "Wind", "lightgreen"),
        BarField(SimUsageFields.SOLAR, "Solar", "orange"),
        BarField(SimUsageFields.STORAGE, "Storage", "lightblue"),
        BarField(SimOutFields.STORAGE_GAS_CHARGE, "Storage Gas Charge", "silver"),
        BarField(SimOutFields.FIXED_STORAGE_CHARGE, "Storage Solar Charge", "gold"),
        BarField(SimOutFields.CURTAILED_ENERGY, "Curtailed Energy", "yellow"),
    ]

    bars_sum = sum((df[field.name] for field in fields))

    max_tick = math.ceil(bars_sum.max() / TICK_STEP) * TICK_STEP

    tickvals = list(np.arange(0, max_tick, TICK_STEP))

    f = barplot(df, fields, year, day_of_year)
    f.update_layout(
        height=800,
        polar=dict(
            hole=0.4,
            radialaxis=dict(
                visible=True,
                range=[0, max_tick],
                tickvals=tickvals,
                tickfont=dict(color="black"),
                tickangle=30,
            ),
            angularaxis=dict(tickfont_size=12, rotation=270, direction="clockwise"),
        ),
        showlegend=True,
    )

    return f


def heatmap(df: pd.DataFrame, name: str, pallette):
    df_by_date = df.groupby(["date"]).sum()

    f = go.Figure(
        go.Heatmap(z=[df_by_date[name]], showscale=False, colorscale=pallette)
    )
    f.update_layout(
        showlegend=False,
        height=30,
        xaxis={"fixedrange": True, "visible": False},
        yaxis={"fixedrange": True, "visible": False},
        margin=dict(l=28, r=25, t=0, b=0),
    )
    return f


def calculate_daily_usage_data(params: "AllParams") -> list[pd.DataFrame]:
    r = Roadmap(
        start_year=params.general.start_year,
        end_year=params.general.end_year,
        solar_capacity_kw=RoadmapParam(
            start=4_000, end_min=150_000, end_max=250_000, step=20_000
        ),
        wind_capacity_kw=RoadmapParam(start=80, end_min=250, end_max=3_000, step=100),
        storage_capacity_kwh=RoadmapParam(
            start=0, end_min=50_000, end_max=400_000, step=50_000
        ),
        storage_efficiency=RoadmapParam(
            start=0.85,
            end_min=0.9,
            end_max=0.95,
            step=0.05,
        ),
        storage_min_energy_rate=RoadmapParam(start=0.2, end_min=0.05, end_max=0.1, step=0.05),
    )

    scenario = next(r.scenarios)
    res = run_scenario(scenario, params)

    for i, df in enumerate(res):
        date_nums = (df.index.to_series() // 24)
        df["date"] = date_nums.apply(str)

    return res


def daily_page(app: "Dash", params: "AllParams") -> Page:
    plot_div_id = comp_id("plot_div")
    update_btn = comp_id("update_btn")
    year_slider = comp_id("year_slider")
    day_slider = comp_id("dy_slider")
    heat_maps = comp_id("heat_maps")

    @app.callback(
        Output(plot_div_id, "figure"),
        Output(heat_maps, "children"),
        Input(update_btn, "n_clicks"),
        Input(year_slider, "value"),
        Input(day_slider, "value"),
        prevent_initial_call=True,
    )
    def calc(_n_clicks: int, year: int, day_of_year: int):
        global sim_results

        if ctx.triggered_id == update_btn:
            sim_results = calculate_daily_usage_data(params)

        year_idx = year - params.general.start_year
        df = sim_results[year_idx]

        df[ONLY_SOLAR] = (
                df[SimOutFields.SOLAR_USAGE]
                + df[SimOutFields.CURTAILED_ENERGY]
                + df[EnergySource.STORAGE]
        )

        polar_plot = plot(df, year, day_of_year)

        demand_title = html.H5("Energy Demand", style={"textAlign": "center"})
        demand_heatmap = dcc.Graph(
            figure=heatmap(df, SimOutFields.DEMAND, "reds"),
            config={"displayModeBar": False},
        )
        solar_title = html.H5("Solar Generation", style={"textAlign": "center"})
        solar_heatmap = dcc.Graph(
            figure=heatmap(
                df,
                ONLY_SOLAR,
                [[0, "white"], [0.8, "gold"], [1, "orange"]],
            ),
            config={"displayModeBar": False},
        )

        heatmaps = [demand_title, demand_heatmap, solar_title, solar_heatmap]

        return polar_plot, heatmaps

    return Page(
        title="Daily Generation",
        layout=html.Div(
            [
                dbc.Button(id=update_btn, class_name="m-3", children="Update"),
                html.H1(
                    "Daily generation and consumption", style={"textAlign": "center"}
                ),
                html.Div(id=heat_maps, style={"position": "relative"}),
                html.Div(
                    style={"width": "100%"},
                    children=[
                        dcc.Slider(
                            min=0,
                            max=DAYS_IN_YEAR - 1,
                            step=1,
                            value=339,
                            marks=month_marks(),
                            id=day_slider,
                        ),
                    ],
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            [
                                dcc.Slider(
                                    min=params.general.start_year,
                                    # the year range is exclusive
                                    max=params.general.end_year - 1,
                                    step=1,
                                    value=params.general.end_year - 1,
                                    marks=year_marks(params.general.start_year, params.general.end_year - 1),
                                    id=year_slider,
                                    vertical=True,
                                    verticalHeight=600,
                                )
                            ],
                            style={"width": "7%", "display": "inline-block"},
                        ),
                        html.Div(
                            dcc.Graph(id=plot_div_id, config={"displayModeBar": False}),
                            style={
                                "width": "90%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                    ],
                ),
            ]
        ),
    )
