import dash_bootstrap_components as dbc
from dash import Dash

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

    app.layout = rm.dash_editor(
        app,
        'Roadmaps',
        'Enter ranges of predicted values to create a variety of feature scenarios.'
    )

    app.run(debug=True)
