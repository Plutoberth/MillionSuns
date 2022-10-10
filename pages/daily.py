import math
import typing as t

import datetime

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, ctx, dcc, html

from dash_models import Page
from dash_models.utils import comp_id

from params.roadmap import Roadmap, RoadmapParam
from common import EnergySource, SimOutFields, SimUsageFields
from scenario_evaluator.run_scenarios import run_scenario

import numpy as np

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import AllParams
    from dash import Dash

SPAN = "</span>"
BR = "<br>"
ONLY_SOLAR = "onlysolar"
TICK_STEP = 20000
DAYS_IN_YEAR = 365

theta = [f"{n}:00" for n in range(24)]
no_fill_theta = list(theta)
no_fill_theta.append(theta[0])
width = [1] * 24


def polar_bar(df: pd.DataFrame, day: int, row_name: str, label: str, color: str):
    r = df[row_name][(day * 24): (day + 1) * 24]
    return go.Barpolar(
        name=label,
        r=r,
        theta=theta,
        width=width,
        marker_color=color,
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
    return (
            "<span style='font-weight:bolder;color:black;font-size: 20px'>"
            + date_str(year, day_of_year)
            + SPAN
            + BR
            + BR
            + "<span style='color:red';font-size: 16px>Total Demand: {:.2f} "
              "KWh".format(df_by_date[SimOutFields.DEMAND][day_of_year] / 1000)
            + SPAN
            + BR
            + "<span style='color:orange;font-size: 16px'>Solar Power: {:.2f} "
              "KWh".format(df_by_date[ONLY_SOLAR][day_of_year] / 1000) + SPAN + BR
    )


def barplot(df: pd.DataFrame, year: int, day_of_year: int):
    f = go.Figure()

    f.add_trace(polar_bar(df, day_of_year, SimUsageFields.COAL, "Coal", "black"))
    f.add_trace(polar_bar(df, day_of_year, SimUsageFields.GAS, "Gas", "lightgray"))
    f.add_trace(polar_bar(df, day_of_year, SimUsageFields.WIND, "Wind", "lightgreen"))
    f.add_trace(polar_bar(df, day_of_year, SimUsageFields.SOLAR, "Solar", "orange"))
    f.add_trace(polar_bar(df, day_of_year, SimUsageFields.STORAGE, "Storage", "lightblue"))
    f.add_trace(polar_bar(df, day_of_year, SimOutFields.STORAGE_GAS_CHARGE, "Storage Gas Charge", "silver"))
    f.add_trace(polar_bar(df, day_of_year, SimOutFields.FIXED_STORAGE_CHARGE, "Storage Solar Charge", "gold"))
    f.add_trace(polar_bar(df, day_of_year, SimOutFields.CURTAILED_ENERGY, "Curtailed Energy", "yellow"))
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
    df[ONLY_SOLAR] = (
            df[SimOutFields.SOLAR_USAGE]
            + df[SimOutFields.CURTAILED_ENERGY]
            + df[EnergySource.STORAGE]
    )
    # TODO: not sure that this calculation is good
    df["discharge"] = (
            df[EnergySource.COAL]
            + df[SimOutFields.GAS_USAGE]
            + df[SimOutFields.STORAGE_GAS_CHARGE]
            + df[EnergySource.WIND]
            + df[SimOutFields.SOLAR_USAGE]
            + df[SimOutFields.FIXED_STORAGE_CHARGE]
            + df[SimOutFields.CURTAILED_ENERGY]
            + df[EnergySource.STORAGE]
    )

    max_tick = math.ceil(df["discharge"].max() / TICK_STEP) * TICK_STEP

    tickvals = [i * TICK_STEP for i in range(1, int(max_tick / TICK_STEP))]

    f = barplot(df, year, day_of_year)
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


def month_marks():
    # year hardly matters, except leap years
    _year = 2020

    result = {}
    for month in range(12):
        timestamp = pd.Timestamp(_year, month + 1, 1)
        day = timestamp.dayofyear
        result[day] = "|"
        result[day + 15] = timestamp.month_name()
    result[pd.Timestamp(_year, 12, 31).dayofyear - 1] = "|"
    return result


def year_marks(minimum, maximum):
    marked_years = filter(lambda x: x % 10 == 0, range(minimum, maximum + 1))
    marked_years = list(marked_years)

    # ensure end and start year are present
    if maximum != marked_years[-1]:
        marked_years.append(maximum)

    if minimum != marked_years[0]:
        marked_years.append(minimum)

    return {y: str(y) for y in marked_years}


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
        storage_discharge=RoadmapParam(start=0.8, end_min=0.9, end_max=0.95, step=0.05),
    )

    scenario = next(r.scenarios)
    res = run_scenario(scenario, params)

    for i, df in enumerate(res):
        date_nums = (df.index.to_series() // 24)
        df["date"] = date_nums.apply(str)

    return res


df_list: list[pd.DataFrame] | None = None


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
        global df_list

        if ctx.triggered_id == update_btn:
            df_list = calculate_daily_usage_data(params)

        year_idx = year - params.general.start_year
        df = df_list[year_idx]

        return plot(df, year, day_of_year), [
            html.H5("Energy Demand", style={"textAlign": "center"}),
            dcc.Graph(
                figure=heatmap(df, SimOutFields.DEMAND, "reds"),
                config={"displayModeBar": False},
            ),
            html.H5("Solar Generation", style={"textAlign": "center"}),
            dcc.Graph(
                figure=heatmap(
                    df,
                    ONLY_SOLAR,
                    [[0, "white"], [0.8, "gold"], [1, "orange"]],
                ),
                config={"displayModeBar": False},
            ),
        ]

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
