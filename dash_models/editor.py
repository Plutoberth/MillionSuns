"""
----

Editor
======

``DashEditorPage``
------------------

Like ``DashModel`` but with an accompanying JSON editor for the model.
Intended to be used with a top level model as a full page.

----
"""

__all__ = ("DashEditorPage",)

import base64
import json
import typing as t

import dash_ace
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, dcc

from .model import DashModel
from .utils import comp_id

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component

JSON_DUMPS_KWARGS = dict(indent=2)


class DashEditorPage(DashModel):
    """
    Like ``DashModel`` but with an accompanying JSON editor for the model.
    Intended to be used with a top level model as a full page.
    """

    def dash_editor(self, app: "Dash", title: str, desc: str) -> "Component":

        """
        Create a collapse card and JSON editor fo the model.

        The editors `Update` button will be propagated to all underlying models,
        to allow propagation of edits.

        :param app: `Dash` to add callbacks to.
        :param title: Text for collapse toggle button.
        :param desc: Text under collapse toggle button.
        :return: Containing component.
        """
    ui_tab = comp_id("ui_tab")
    json_sub = comp_id("json_sub")
    json_up = comp_id("json_up")
    json_down_btn = comp_id("json_down_btn")
    json_down = comp_id("json_down")
    json_ref = comp_id("json_ref")
    json_ace = comp_id("json_ace")

    @app.callback(
        Output(json_sub, "key"),  # just need some output
        Input(json_sub, "n_clicks"),
        State(json_ace, "value"),
        prevent_initial_call=True,
    )
    def update_from_json(n_clicks: int, value: str):
        if value != self.json(**JSON_DUMPS_KWARGS):
            self.update(json.loads(value))
            return self.json()

        @app.callback(
            Output(json_ace, "value"),
            Input(json_up, "contents"),
            Input(json_ref, "n_clicks"),
            prevent_initial_call=True,
        )
        def upload_params_jsons(content: str, n_clicks: int):
            if ctx.triggered_id == json_up and content:

    _, content_encoded = content.split(",")
    return base64.b64decode(content_encoded).decode("utf-8")

    if ctx.triggered_id == json_ref:
        return self.json(**JSON_DUMPS_KWARGS)

        @app.callback(
            Output(json_down, "data"),
            Input(json_down_btn, "n_clicks"),
            State(json_ace, "value"),
            prevent_initial_call=True,
        )
        def download_params_jsons(n_clicks: int, value: str):
            return dcc.send_string(value, f"{title}.json", "text/json")

        return dbc.Tabs(
            children=[
                dbc.Tab(
                    id=ui_tab,
                    label="UI Editor",
                    children=self.dash_collapse(app, title, desc, json_sub),
                ),
                dbc.Tab(
                    label="JSON Editor",
                    children=[
                        dbc.Container(
                            class_name="d-flex flex-row justify-content-center",
                            children=[
                                dbc.Button(
                                    id=json_sub, class_name="m-2", children="Submit"
                                ),
                                dbc.Button(
                                    id=json_ref, class_name="m-2", children="Refresh"
                                ),
                                dcc.Upload(
                                    id=json_up,
                                    className="btn btn-primary m-2",
                                    children="Upload",
                                ),
                                dbc.Button(
                                    id=json_down_btn,
                                    class_name="m-2",
                                    children="Download",
                                ),
                                dcc.Download(id=json_down),
                            ],
                        ),
                        dash_ace.DashAceEditor(
                            id=json_ace,
                            value=self.json(**JSON_DUMPS_KWARGS),
                            theme="monokai",
                            mode="json",
                            enableBasicAutocompletion=True,
                            enableLiveAutocompletion=True,
                            fontSize=18,
                            style={
                                "font-family": "monospace, monospace",
                                "width": "100%",
                            },
                        ),
                    ],
                ),
            ]
        )
