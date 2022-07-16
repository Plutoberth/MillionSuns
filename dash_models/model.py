import typing as t

import dash_bootstrap_components as dbc
import typing_inspect as ti
from dash import Input, Output, State
from pydantic import BaseModel

from .utils import comp_id

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component
    from pydantic.fields import ModelField


class DashModel(BaseModel):
    @staticmethod
    def _label(title: str):
        return dbc.Label(
            class_name='mt-2',
            children=title
        )

    def _input(self, app: 'Dash', field: 'ModelField', update_btn_id: str, **kwargs):
        inp_id = comp_id('input')

        @app.callback(
            Output(inp_id, 'key'),
            Input(inp_id, 'value')
        )
        def int_update(value: t.Any):
            setattr(self, field.name, field.type_(value))
            return inp_id

        @app.callback(
            Output(inp_id, 'value'),
            Input(update_btn_id, 'n_clicks'),
            prevent_initial_call=True
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

    def _labeled_input(self, app: 'Dash', field: 'ModelField', update_btn_id: str, **kwargs):
        return dbc.Container(
            [
                self._label(field.field_info.title or field.name.replace('_', ' ').title()),
                self._input(
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
        attr = getattr(self, field.name)

        if ti.is_literal_type(field.type_):
            return dbc.Container()
        elif issubclass(field.type_, int):
            return self._labeled_input(
                app,
                field,
                update_btn_id,
                type='number',
                step=1
            )
        elif issubclass(field.type_, float):
            return self._labeled_input(
                app,
                field,
                update_btn_id,
                type='number',
                step=0.005
            )
        elif issubclass(field.type_, DashModel):
            return attr.dash_collapse(
                app,
                field.field_info.title or field.name.replace('_', ' ').title(),
                field.field_info.description,
                update_btn_id
            )
        else:
            raise NotImplementedError(
                f'The field {field.name}'
                f' has type {field.type_!r}'
                f' which is not yet supported'
            )

    def update(self, data: dict[str, t.Any]):
        for k, v in data.items():
            if isinstance(attr := getattr(self, k), DashModel):
                attr.update(v)
            else:
                setattr(self, k, v)

    def dash_fields(
        self,
        app: 'Dash',
        update_btn_id: str
    ) -> 'Component':
        return dbc.Container(
            list(
                map(
                    lambda field: self._component(app, field, update_btn_id),
                    self.__fields__.values()
                )
            )
        )

    def dash_collapse(
        self,
        app: 'Dash',
        title: str,
        desc: str,
        update_btn_id: str
    ) -> 'Component':
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
                    children=self.dash_fields(app, update_btn_id)
                )
            ]
        )

    class Config:
        validate_all = True
        validate_assignment = True
        underscore_attrs_are_private = True
