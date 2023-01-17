import logging

import dash_bootstrap_components as dbc
from dash import Dash, html

from dash_models import Brand, Page, navbar_page
from data.defaults import DEFAULT_PARAMS
from pages import make_pages
from params import AllParams

LOG_FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
logging.info("Starting application")

app = Dash(
    __name__,
    title="NZO - 95% by 2050",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
)

params = AllParams(**DEFAULT_PARAMS)

p_home = Page(
    title="Home",
    layout=dbc.Container(
        class_name="d-flex flex-column justify-content-center align-items-center",
        children=[
            html.H1("NZOs' Roadmap To 2050"),
            html.H5(
                "Use the Parameters page to edit or upload the model parameters,"
                " then head over to the other pages to generate the graphs."
            ),
            html.Strong(
                "Note: The app can sometimes be slow."
                " Please wait 2-3 seconds before pressing a button for the second time."
            ),
        ],
    ),
)

b_nzo = Brand(img="nzo.png", href="https://www.nzo.org.il/")

b_aman = Brand(img="aman.png", href="https://youtu.be/5a15k3_6PAo")

app.layout = navbar_page(
    app,
    p_home,
    make_pages(app, params),
    (b_nzo, b_aman),
    color="dark",
    style={"color":"white"},
    dark=True,
)

if __name__ == "__main__":
    app.run(debug=True)
