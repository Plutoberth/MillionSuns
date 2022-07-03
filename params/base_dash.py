"""
----

Dash integration
================

``BaseDash``
------------

Integrate object with plotly ``Dash``.

- Get component representing object using ``.dash(app) -> Component``.

----
"""

__all__ = 'BaseDash',

import typing as t

from pydantic import BaseModel

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class BaseDash(BaseModel):
    """ Integrate object with plotly Dash. """

    def dash(self, app: 'Dash') -> 'Component':
        """
        Get a plotly Dash component representing the object.

        Appropriate callbacks will be added to the given app.
        """
        ...
