import dash_bootstrap_components as dbc
from dash import Dash

from params import Params

if __name__ == '__main__':
    params_json = {
        'start_year': 2020,
        'end_year': 2050,
        'population': [
            {
                'start_year': 2020,
                'end_year': 2050,
                'interpo': {
                    'type': 'constant',
                    'value': 10.
                }
            }
        ],
    }

    params = Params(**params_json)

    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME,
        ],
        external_scripts=[
            'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js',
        ]
    )

    app.layout = params.dash_editor(
        app,
        'Params',
        'Enter ranges of interpolated predictions,'
        ' which will be combined with 2018 data,'
        ' to simulate energy production and usage in the future.'
    )

    app.run(debug=True)
