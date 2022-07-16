"""
----

List
====

``DashListable``
----------------

Base class for models that are intended as items in a `DashList`.

``DashList``
------------

Generic base class with a list __root__,
includes add and remove buttons to edit the list.

----
"""

__all__ = 'DashListable', 'DashList'

import typing as t
from abc import ABC, abstractmethod

import dash_bootstrap_components as dbc
from dash import Input, Output, ctx, html
from pydantic.generics import GenericModel

from .model import DashModel
from .utils import comp_id

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class DashListable(DashModel, ABC):
    """
    Base class for models that are intended as items in a `DashList`.
    """

    @property
    @abstractmethod
    def title(self) -> str:
        """ Create a title for the item """
        ...

    class Config:
        copy_on_model_validation = False


TListable = t.TypeVar('TListable', bound=DashListable)


class DashList(DashModel, GenericModel, t.Generic[TListable]):
    """
    Generic base class with a list __root__,
    includes add and remove buttons to edit the list.
    """
    __root__: list[TListable] = []
    __root_fields__: list['Component']

    # all layouts must be generated in advance,
    # so we will keep unused ones here
    __disabled__: list[TListable]
    __disabled_fields__: list['Component']

    _max_items: int = 5
    """Intended to be overridden if needed"""

    # ^ really PyCharm? You can't a comment above as the docs?

    def update(self, data: list[t.Any]):

        # move items in or out if __disabled__ as needed

        while len(data) > len(self.__root__):
            self.__root__.append(self.__disabled__.pop())
            self.__root_fields__.append(self.__disabled_fields__.pop())

        while len(data) > len(self.__root__):
            self.__disabled__.append(self.__root__.pop())
            self.__disabled_fields__.append(self.__root_fields__.pop())

        for idx, item in enumerate(data):
            self.__root__[idx].update(item)

    def dash_fields(
        self,
        app: 'Dash',
        update_btn_id: str
    ) -> 'Component':

        # initial generation of the fields and other stuff.
        # possible because if this method is called again everything breaks anyway.

        self.__root_fields__ = [
            item.dash_fields(app, update_btn_id)
            for item in self.__root__
        ]

        # find runtime value of TListable.
        # this is quite janky, but python does not have a good type hint API.
        listable_type: t.Type[TListable] = t.get_args(t.get_type_hints(type(self))['__root__'])[0]

        self.__disabled__ = [
            listable_type()
            for _ in range(self._max_items - len(self.__root__))
        ]
        self.__disabled_fields__ = [
            item.dash_fields(app, update_btn_id)
            for item in self.__disabled__
        ]

        cont_id = comp_id('container')
        acc_id = comp_id('accordion')
        acc_item_id_type = comp_id('acc_item')
        acc_item_ids = [
            {'type': acc_item_id_type, 'index': idx}
            for idx in range(self._max_items)
        ]
        add_id = comp_id('add')
        sub_id = comp_id('sub')

        def _accordion():
            return dbc.Container(
                [
                    dbc.Collapse(
                        is_open=False,
                        children=self.__disabled_fields__
                    ),
                    dbc.Accordion(
                        id=acc_id,
                        class_name='mt-2',
                        start_collapsed=True,
                        always_open=True,
                        children=[
                            dbc.AccordionItem(
                                id=id_,
                                title=item.title,
                                children=fields
                            )
                            for id_, item, fields
                            in zip(acc_item_ids, self.__root__, self.__root_fields__)
                        ]
                    )
                ]
            )

        @app.callback(
            Output(cont_id, 'children'),
            Input(update_btn_id, 'n_clicks'),
            Input(add_id, 'n_clicks'),
            Input(sub_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def update(update_n_clicks: int, add_n_clicks: int, sub_n_clicks: int):
            if ctx.triggered_id == add_id:
                self.__root__.append(self.__disabled__.pop())
                self.__root_fields__.append(self.__disabled_fields__.pop())
            elif ctx.triggered_id == sub_id:
                self.__disabled__.append(self.__root__.pop())
                self.__disabled_fields__.append(self.__root_fields__.pop())

            return _accordion()

        return dbc.Container(
            children=[
                dbc.Button(
                    id=add_id,
                    class_name='m-2',
                    children=html.I(className='fa fa-plus')
                ),
                dbc.Button(
                    id=sub_id,
                    class_name='m-2',
                    children=html.I(className='fa fa-minus')
                ),
                dbc.Container(
                    id=cont_id,
                    children=_accordion()
                )
            ]
        )
