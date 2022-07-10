"""
----

Model parameters
================

``Params``
----------

All parameters of the model.

Each ``InterpolatedParam`` is a known attribute for editor completion,
from which a ``params: list[InterpolatedParam]`` is generated for iteration.

As such, this is not completely generalized,
in the sense that new parameters need to be added manually.

----
"""

from pydantic import PositiveInt, PrivateAttr

from .base_dash_model import DashModel
from .interpolated_param import InterpolatedParam


class Params(DashModel):
    start_year: PositiveInt
    end_year: PositiveInt

    population: InterpolatedParam
    # solar_panel_price: InterpolatedParam

    params: dict[str, Param] | None = Field(exclude=True)

    @validator(
        'population',
        'solar_panel_price',
        pre=True
    )
    def inject_years(cls, param: dict, values: dict) -> Param:
        return Param(
            **param,
            start_year=values['start_year'],
            end_year=values['end_year']
        )

    @validator('params', always=True)
    def gen_params(cls, v: None, values: dict[str, PositiveInt | Param]):
        return {
            name: attr
            for name, attr in values.items()
            if isinstance(attr, Param)
        }

    def dash(self, app: 'Dash') -> 'Component':
        return dbc.Accordion(
            always_open=True,
            start_collapsed=True,
            children=[
                dbc.AccordionItem(
                    title=f'{to_title(name)} ({param.unit})',
                    children=param.dash(app)
                ) for name, param in self.params.items()
            ]
        )
