import typing as t
from secrets import token_hex

import dash_bootstrap_components as dbc
from dash import Input, Output, State
from pydantic import BaseModel

if t.TYPE_CHECKING:
    from dash import Dash
    from pydantic.fields import ModelField
    from dash.development.base_component import Component


def comp_id(s: str) -> str:
    return f'bdm__{s}__{token_hex(8)}'


class BaseDashModel(BaseModel):
    def __input(self, app: 'Dash', field: 'ModelField', update_btn_id: str, **kwargs):
        inp_id = comp_id('input')

        @app.callback(
            Output(inp_id, 'key'),
            Input(inp_id, 'value')
        )
        def int_update(value: t.Any):
            setattr(self, field.name, value)
            return inp_id

        @app.callback(
            Output(inp_id, 'value'),
            Input(update_btn_id, 'n_clicks')
        )
        def ext_update(n_clicks: int):
            return getattr(self, field.name)

        return dbc.Input(
            id=inp_id,
            min=field.field_info.le or field.field_info.lt,
            max=field.field_info.ge or field.field_info.gt,
            value=getattr(self, field.name),
            **kwargs
        )

    def __labeled_input(self, app: 'Dash', field: 'ModelField', update_btn_id: str, **kwargs):
        return dbc.Container(
            [
                dbc.Label(
                    class_name='mt-2',
                    children=field.field_info.title
                ),
                self.__input(
                    app,
                    field,
                    update_btn_id,
                    **kwargs
                )
            ]
        )

    def _component(
        self,
        app: 'Dash',
        field: 'ModelField',
        update_btn_id: str
    ) -> 'Component':
        if issubclass(field.type_, BaseDashModel):
            return getattr(self, field.name).dash(
                app,
                field.field_info.title or field.name.replace('_', ' ').title(),
                field.field_info.description,
                update_btn_id
            )
        elif issubclass(field.type_, int):
            return self.__labeled_input(
                app,
                field,
                update_btn_id,
                type='number',
                step=1
            )
        elif issubclass(field.type_, float):
            return self.__labeled_input(
                app,
                field,
                update_btn_id,
                type='number',
                step=0.005
            )

    def dash(self, app: 'Dash', title: str, desc: str, update_btn_id: str) -> 'Component':
        btn_id = comp_id('collapse_btn')
        coll_id = comp_id('collapse')

        @app.callback(
            Output(coll_id, 'is_open'),
            Input(btn_id, 'n_clicks'),
            State(coll_id, 'is_open'),
            prevent_initial_call=True
        )
        def update_collapse(n_clicks: int, is_open: bool):
            return not is_open

        return dbc.Card(
            class_name='p-3 m-3',
            children=[
                dbc.Button(
                    id=btn_id,
                    children=title
                ),
                dbc.Container(class_name='text-muted text-center', children=desc),
                dbc.Collapse(
                    id=coll_id,
                    children=list(
                        map(
                            lambda field: self._component(app, field, update_btn_id),
                            self.__fields__.values()
                        )
                    )
                )
            ],
        )
