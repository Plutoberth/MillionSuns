import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html

from params import Params

if __name__ == '__main__':
    params_json = {
        'start_year': 2020,
        'end_year': 2050,
        'population': {
            'unit': 'M',
            'ranges': [
                {
                    'enabled': True,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                }
            ]
        },
        'solar_panel_price': {
            'unit': 'USD/Kw',
            'ranges': [
                {
                    'enabled': True,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                },
                {
                    'enabled': False,
                    'start_year': 2020,
                    'end_year': 2050,
                    'interpo': {
                        'type': 'constant',
                        'value': 10
                    }
                }
            ]
        }
    }

    params = Params(**params_json)

    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP,
        ],
        external_scripts=[
            'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js',
        ],
        suppress_callback_exceptions=True
    )

    app.layout = html.Div(
        [
            params.dash(app),
            dbc.Button('Show JSON', id='json-btn'),
            dbc.Collapse(
                id='collapse',
                children=[
                    dbc.Textarea(id='ta', rows=20),
                    dbc.Button('Update', id='update-btn')
                ]
            ),
        ]
    )


    @app.callback(
        Output('collapse', 'is_open'),
        Input('json-btn', 'n_clicks')
    )
    def update_ta(n_click: int):
        return n_click and n_click % 2 == 1


    @app.callback(
        Output('ta', 'value'),
        Input('update-btn', 'n_clicks')
    )
    def update_ta(n_click: int):
        return params.json(indent=4)


    app.run(debug=True)
