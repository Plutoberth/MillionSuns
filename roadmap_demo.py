import base64
import json
import typing as t

import dash_ace
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc

from params.base_dash_model import BaseDashModel
from params.roadmap import Roadmap

if __name__ == '__main__':
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP,
        ],
        external_scripts=[
            'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js'
        ]
    )

    rm = Roadmap(
        **{
            'start_year': 2020,
            'end_year': 2050,
            'solar_gen_kw': {
                'start': 4000.,
                'end_min': 50_000.,
                'end_max': 150_000.,
                'step': 20_000.
            },
            'wind_gen_kw': {
                'start': 80.,
                'end_min': 250.,
                'end_max': 3000.,
                'step': 100.  # 250 does not make sense
            },
            'storage_cap_kwh': {
                'start': 0.,
                'end_min': 50_000.,
                'end_max': 400_000.,
                'step': 50_000.
            },
            'storage_efficiency_p': {
                'start': .9,
                'end_min': .95,
                'end_max': .95,
                'step': .04  # .05 is exact, floats are not
            },
            'storage_discharge_p': {
                'start': .8,
                'end_min': .9,
                'end_max': .9,
                'step': .05
            },
        }
    )

    ui_tab = 'ui_tab'
    json_sub = 'json_sub'
    json_up = 'json_up'
    json_down_btn = 'json_down_btn'
    json_down = 'json_down'
    json_ref = 'json_ref'
    json_ta = 'json_ta'

    rm_args = (
        app,
        'Roadmaps',
        'Enter ranges of predicted values to create a variety of feature scenarios.',
        json_sub
    )


    def deep_model_update(model: BaseDashModel, update_dict: dict[str, t.Any]):
        for k, v in update_dict.items():
            setattr(
                model,
                k,
                deep_model_update(getattr(model, k), v)
                if isinstance(v, dict)
                else v
            )
        return model


    @app.callback(
        Output(json_sub, 'key'),  # just need some output
        Input(json_sub, 'n_clicks'),
        State(json_ta, 'value')
    )
    def update_from_json(n_clicks: int, value: str):
        if value != rm.json(indent=4):
            deep_model_update(rm, json.loads(value))
        return rm.json()


    @app.callback(
        Output(json_ta, 'value'),
        Input(json_up, 'contents'),
        Input(json_ref, 'n_clicks'),
        prevent_initial_call=True
    )
    def upload_params_jsons(content: str, n_clicks: int):
        if ctx.triggered_id == json_up and content:
            _, content_encoded = content.split(',')
            return base64.b64decode(content_encoded).decode('utf-8')

        if ctx.triggered_id == json_ref:
            return rm.json(indent=4)


    @app.callback(
        Output(json_down, 'data'),
        Input(json_down_btn, 'n_clicks'),
        State(json_ta, 'value'),
        prevent_initial_call=True
    )
    def download_params_jsons(n_clicks: int, value: str):
        print(value)
        # return dcc.send_string(ta_value, PARAMS_JSONS_FILE_NAME, 'text/json')


    app.layout = dbc.Tabs(
        children=[
            dbc.Tab(id=ui_tab, children=[rm.dash(*rm_args)], label='UI Editor'),
            dbc.Tab(
                label='JSON Editor',
                children=[
                    dbc.Container(
                        class_name='d-flex flex-row justify-content-center',
                        children=[
                            dbc.Button(
                                id=json_sub,
                                class_name='m-2',
                                children='Submit'
                            ),
                            dbc.Button(
                                id=json_ref,
                                class_name='m-2',
                                children='Refresh'
                            ),
                            dcc.Upload(
                                id=json_up,
                                className='btn btn-primary m-2',
                                children='Upload'
                            ),
                            dbc.Button(
                                id=json_down_btn,
                                class_name='m-2',
                                children='Download'
                            ),
                            dcc.Download(id=json_down)
                        ]
                    ),
                    dash_ace.DashAceEditor(
                        id=json_ta,
                        value=rm.json(indent=4),
                        theme='monokai',
                        mode='json',
                        enableBasicAutocompletion=True,
                        enableLiveAutocompletion=True,
                        fontSize=18,
                        style={'font-family': 'monospace, monospace'}
                    )
                ]
            )
        ]
    )

    app.run(debug=True)
