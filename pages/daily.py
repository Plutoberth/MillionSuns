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
from enums import EnergySource, SimHourField
from scenario_evaluator.run_scenarios import run_scenario

if t.TYPE_CHECKING:
    from plotly.graph_objs import Figure
    from params import AllParams
    from dash import Dash

SPAN = "</span>"
BR = "<br>"
ONLY_SOLAR = "onlysolar"
TICK_STEP = 20000

theta = [f"{n}:00" for n in range(24)]
no_fill_theta = list(theta)
no_fill_theta.append(theta[0])
width = [1] * 24


def polar_bar(df, day, name, color):
    r = df[name][(day * 24) : (day + 1) * 24]
    return go.Barpolar(
        name=str(name),
        r=r,
        theta=theta,
        width=width,
        marker_color=color,
        hovertemplate="<i>%{theta} : %{r:,.0f} KW</i>",
    )


def polar_scatter(df, day, name, color, fill=True, dash=False):
    r = df[name][(day * 24) : (day + 1) * 24]
    if not fill:  # if fill is false then add another point to close the loop
        r = list(r)
        r.append(r[0])
    return go.Scatterpolar(
        name=str(name),
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


def date_str(df: pd.DataFrame, day_of_year: int):
    # TODO: remove hardcoded 2020 so it's less ugly
    date = datetime.datetime(2020, 1, 1) + datetime.timedelta(day_of_year - 1)
    return date.strftime("%d %B")

def annotation(df: pd.DataFrame, day_of_year: int):
    df_by_date = df.groupby(["date"]).sum()
    return (
        "<span style='font-weight:bolder;color:black;font-size: 20px'>"
        + date_str(df, day_of_year)
        + SPAN
        + BR
        + BR
        + "<span style='color:red';font-size: 16px>Total Demand: {:.2f} "
        "KWh".format(df_by_date[SimHourField.DEMAND][day_of_year] / 1000)
        + SPAN
        + BR
        + "<span style='color:orange;font-size: 16px'>Solar Power: {:.2f} "
        "KWh".format(df_by_date[ONLY_SOLAR][day_of_year] / 1000) + SPAN + BR
    )


def barplot(df: pd.DataFrame, day_of_year: int):
    f = go.Figure()
    f.add_trace(polar_bar(df, day_of_year, EnergySource.COAL, "black"))
    f.add_trace(polar_bar(df, day_of_year, EnergySource.GAS, "lightgray"))
    f.add_trace(polar_bar(df, day_of_year, EnergySource.WIND, "lightgreen"))
    f.add_trace(polar_bar(df, day_of_year, SimHourField.SOLAR_USAGE, "orange"))
    f.add_trace(polar_bar(df, day_of_year, EnergySource.STORAGE, "lightblue"))
    f.add_trace(polar_bar(df, day_of_year, SimHourField.STORAGE_GAS_CHARGE, "silver"))
    f.add_trace(polar_bar(df, day_of_year, SimHourField.STORAGE_SOLAR_CHARGE, "gold"))
    f.add_trace(polar_bar(df, day_of_year, SimHourField.CURTAILED_ENERGY, "yellow"))
    f.add_trace(polar_scatter(df, day_of_year, SimHourField.DEMAND, "red", False))
    f.add_trace(polar_scatter(df, day_of_year, SimHourField.NET_DEMAND, "purple", False, True))
    f.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        text=annotation(df, day_of_year),
        font=dict(family="Arial", size=16, color="black"),
    )
    return f


def plot(df: pd.DataFrame, day_of_year: int):
    df[ONLY_SOLAR] = df[SimHourField.SOLAR_USAGE] + df[SimHourField.CURTAILED_ENERGY] + df[EnergySource.STORAGE]
    df["discharge"] = (
        df[EnergySource.COAL]
        + df[SimHourField.GAS_USAGE]
        + df[SimHourField.STORAGE_GAS_CHARGE]
        + df[EnergySource.WIND]
        + df[SimHourField.SOLAR_USAGE]
        + df[SimHourField.STORAGE_SOLAR_CHARGE]
        + df[SimHourField.CURTAILED_ENERGY]
        + df[EnergySource.STORAGE]
    )

    max_tick = math.ceil(df["discharge"].max() / TICK_STEP) * TICK_STEP

    tickvals = [i * TICK_STEP for i in range(1, int(max_tick / TICK_STEP))]

    f = barplot(df, day_of_year)
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


def marks(year: int):
    result = {}
    for month in range(1, 13):
        timestamp = pd.Timestamp(year, month, 1)
        day = timestamp.dayofyear
        result[day] = "|"
        result[day + 15] = timestamp.month_name()
    result[pd.Timestamp(year, 12, 31).dayofyear - 1] = "|"
    return result


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
        storage_capacity_kwh=RoadmapParam(start=0, end_min=50_000, end_max=400_000, step=50_000),
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

    # TODO: fix this ugly shit
    for i, df in enumerate(res):
        df["date"] = df.index / 24
        df["date"] = df["date"].apply(str)

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

        idx = year - params.general.start_year
        # TODO: remove this ugly shit
        idx = max(idx - 1, 0)
        df = df_list[idx]

        return plot(df, day_of_year), [
            html.H5("Energy Demand", style={"textAlign": "center"}),
            dcc.Graph(
                figure=heatmap(df, SimHourField.DEMAND, "reds"),
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
                            max=pd.Timestamp(params.general.end_year, 12, 31).dayofyear
                            - 1,
                            step=1,
                            value=pd.Timestamp(params.general.end_year, 6, 1).dayofyear
                            - 1,
                            marks=marks(params.general.end_year),
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
                                    max=params.general.end_year,
                                    step=1,
                                    value=params.general.end_year,
                                    marks={
                                        y: str(y)
                                        for y in range(
                                            params.general.start_year,
                                            params.general.end_year + 1,
                                            10,
                                        )
                                    },
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
