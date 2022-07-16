"""
----

Select
======

``DashSelectable``
------------------

Base class for models that are intended as options in ``DashSelect``.

``DashSelect``
--------------

Generic base class with a variable __root__,
which renders the fields of one of multiple selectable options.

----
"""

__all__ = 'DashSelectable', 'DashSelect'

import typing as t
from abc import ABC

import dash_bootstrap_components as dbc
from dash import Input, MATCH, Output, State, ctx
from pydantic.generics import GenericModel

from .model import DashModel
from .utils import comp_id

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class DashSelectable(DashModel, ABC):
    """
    Base class for models that are intended as options in ``DashSelect``.
    """
    type: str

    class Config:
        copy_on_model_validation = False


TSelectable = t.TypeVar('TSelectable', bound=DashSelectable)


class DashSelect(DashModel, GenericModel, t.Generic[TSelectable]):
    """
    Generic base class with a variable __root__,
    which renders the fields of one of multiple selectable options.

    Add multiple private (starting with _) fields,
     and they will be found and be used as options.
    """
    __root__: TSelectable
    _options: dict[str, TSelectable]
    _selected: str

    def __init__(self, **data):
        super().__init__(**data)

        self._options = {
            name.strip('_'): type_()
            for name, type_
            in self.__annotations__.items()
        }

        for name, opt in self._options.items():
            if type(self.__root__) == type(opt):
                self._selected = name
                self._options[name] = self.__root__
                break
        else:
            raise ValueError(
                'Selected option does not seem to exists.\n'
                f'{self.__root__}\n{self._options=}'
            )

    @property
    def selected(self) -> str:
        """Title of currently selected options"""
        return self._selected

    def update(self, data: dict[str, t.Any]):
        self._selected = data['type']  # assuming valid data of DashSelectable
        self.__root__ = self._options[self._selected]
        self.__root__.update(data)

    def dash_collapse(
        self,
        app: 'Dash',
        title: str,
        desc: str,
        update_btn_id: str
    ) -> 'Component':
        select_id = comp_id('select')
        col_id_type = comp_id('collapse')
        coll_ids = {
            name: {'type': col_id_type, 'name': name}
            for name in self._options
        }

        @app.callback(
            Output({'type': col_id_type, 'name': MATCH}, 'is_open'),
            Input(select_id, 'value'),
            Input(update_btn_id, 'n_clicks'),
            State({'type': col_id_type, 'name': MATCH}, 'id')
        )
        def select(value: str, n_clicks: int, col_id: dict[str, str]):
            if ctx.triggered_id == select_id:
                self._selected = value
                self.__root__ = self._options[self._selected]
            return col_id['name'] == value

        return dbc.Container(
            [
                self._label(title),
                dbc.Select(
                    id=select_id,
                    options=[{'label': opt} for opt in self._options],
                    value=self._selected
                ),
                dbc.Card(
                    class_name='m-2 p-2',
                    children=[
                        dbc.Collapse(
                            id=coll_ids[name],
                            is_open=False,
                            children=opt.dash_fields(
                                app,
                                update_btn_id
                            )
                        )
                        for name, opt in self._options.items()
                    ]
                )
            ]
        )
