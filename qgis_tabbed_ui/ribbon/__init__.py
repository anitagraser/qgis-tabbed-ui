# -*- coding: utf-8 -*-
"""
The ribbon — a QTabWidget styled like a Microsoft Office ribbon, with a tab
per TAB of the tabs package:

widget.py   RibbonWidget, which builds the tabs
groups.py   ribbon groups (framed sections of buttons)
buttons.py  buttons for QGIS actions and their label/icon overrides
actions.py  looking up QGIS actions by entry name
qgis_ui.py  QGIS' own menus and toolbars
styles.py   stylesheets and sizes
"""

from .widget import RibbonWidget

__all__ = ["RibbonWidget"]
