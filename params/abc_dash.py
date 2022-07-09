"""
----

Dash integration
================

``ABCDash``
------------

Integrate object with plotly ``Dash``.

- Get component representing object using ``.dash(app) -> Component``.

----
"""

__all__ = 'ABCDash',

import typing as t

from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class ABCDash(ABC):
    """ Integrate object with plotly Dash. """

    @abstractmethod
    def dash(self, app: 'Dash') -> 'Component':
        """
        Get a plotly Dash component representing the object.

        Appropriate callbacks will be added to the given app.
        """
        ...
