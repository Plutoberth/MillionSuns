import typing as t
from dataclasses import dataclass

import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash.development.base_component import Component

from .utils import comp_id

if t.TYPE_CHECKING:
    from dash import Dash


@dataclass
class Page:
    title: str
    layout: Component


@dataclass
class Brand:
    img: str
    href: str


def title_to_path(s: str) -> str:
    return '/' + s.casefold().lower().replace(' ', '_')


def navbar_page(
    app: 'Dash',
    home_page: Page,
    pages: t.Sequence[Page],
    brands: t.Sequence[Brand],
    **kwargs
) -> 'Component':
    loc_id = comp_id('location')
    cont_id = comp_id('content_container')

    page_map = {title_to_path(page.title): page.layout for page in pages}
    page_map['/'] = home_page.layout

    @app.callback(
        Output(cont_id, 'children'),
        Input(loc_id, 'pathname')
    )
    def choose(pathname: str):
        try:
            return page_map[pathname]
        except KeyError:
            return dbc.Alert(
                color='danger',
                style={
                    'position': 'absolute',
                    'left': '50%',
                    'top': '50%',
                    'transform': 'translate(-50%, -50%)'
                },
                children='404 Page not found'
            )

    return html.Div(
        [
            dcc.Location(
                id=loc_id,
                refresh=False
            ),
            dbc.Navbar(
                **kwargs,
                children=[
                    *[
                        dbc.NavbarBrand(
                            href=brand.href,
                            external_link=True,
                            children=html.Img(
                                className='m-1',
                                height=40,
                                src=app.get_asset_url(brand.img)
                            )
                        )
                        for brand in brands
                    ],
                    dbc.NavLink(
                        href='/',
                        children='Home'
                    ),
                    *[
                        dbc.NavLink(
                            href=title_to_path(page.title),
                            children=page.title
                        )
                        for page in pages
                    ]
                ]
            ),
            html.Div(
                id=cont_id,
                children=home_page.layout
            )
        ]
    )
