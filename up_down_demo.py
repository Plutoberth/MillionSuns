import base64

from dash import Dash, Input, Output, State, dcc, html

app = Dash(
    __name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css'
    ],
    external_scripts=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js',
        'https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.5/dist/umd/popper.min.js'
    ]
)

PARAMS_JSON_ID = 'params_json'
PARAMS_JSON_CARD_ID = 'params_json_card'
PARAMS_JSON_SUBMIT_BTN_ID = 'params_json_submit_btn'
PARAMS_JSON_DOWNLOAD_BTN_ID = 'params_json_down_btn'
PARAMS_JSON_DOWNLOAD_ID = 'params_json_down'
PARAMS_JSON_UPLOAD_ID = 'params_json_up'
PARAMS_JSON_FILE_NAME = 'params.json'

app.layout = html.Div(
    className='',
    children=[
        html.A(
            className='btn btn-primary',
            **{
                'data-bs-toggle': 'collapse',
                'data-bs-target': f'#{PARAMS_JSON_ID}'
            },
            children='JSON'
        ),
        html.Div(
            id=PARAMS_JSON_ID,
            className='collapse',
            children=[
                html.Div(
                    id=PARAMS_JSON_CARD_ID,
                    className='card cord-body'
                ),
                html.Button(
                    id=PARAMS_JSON_SUBMIT_BTN_ID,
                    className='btn btn-primary btn-sm',
                    children='Submit'
                ),
                html.Button(
                    id=PARAMS_JSON_DOWNLOAD_BTN_ID,
                    className='btn btn-outline-primary btn-sm',
                    children='Download'
                ),
                dcc.Upload(
                    id=PARAMS_JSON_UPLOAD_ID,
                    className='btn btn-outline-primary btn-sm',
                    children='Upload'
                ),
                dcc.Download(
                    id=PARAMS_JSON_DOWNLOAD_ID,
                )
            ]
        )
    ]
)


@app.callback(
    Output(PARAMS_JSON_CARD_ID, 'children'),
    Input(PARAMS_JSON_UPLOAD_ID, 'contents'),
    prevent_initial_call=True
)
def upload_params_jsons(content: str):
    if content:
        _, content_encoded = content.split(',')
        return base64.b64decode(content_encoded).decode('utf-8')


@app.callback(
    Output(PARAMS_JSON_DOWNLOAD_ID, 'data'),
    Input(PARAMS_JSON_DOWNLOAD_BTN_ID, 'n_clicks'),
    State(PARAMS_JSON_CARD_ID, 'children'),
    prevent_initial_call=True
)
def download_params_jsons(n_clicks: int, card_children: str):
    print(repr(card_children))
    # return dcc.send_string(ta_value, PARAMS_JSONS_FILE_NAME, 'text/json')


if __name__ == '__main__':
    app.run(debug=True)
