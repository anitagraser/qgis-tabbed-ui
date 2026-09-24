# -*- coding: utf-8 -*-
"""Stylesheets and sizes of the ribbon."""

from qgis.PyQt.QtGui import QPalette

# Button sizes (px)
LARGE_ICON_SIZE = 28
LARGE_BUTTON_WIDTH = 56
LARGE_BUTTON_HEIGHT = 70
SMALL_ICON_SIZE = 18
SMALL_BUTTON_HEIGHT = 22
# Rows of small buttons per column in a group
DEFAULT_ROWS = 3

# Opacity of the window text color used for the dividers between groups
DIVIDER_ALPHA = 0.2


def divider_color(palette):
    """The theme's text color faded over its window color: a subtle line in
    any theme (palette(mid) is far too dark in some)."""
    color = palette.color(QPalette.ColorRole.WindowText)
    color.setAlphaF(DIVIDER_ALPHA)
    return color


# Colors use palette() roles so the ribbon follows the active QGIS theme
# (e.g. Night Mapping) instead of hard-coded light colors. The tabs are left
# unstyled so they look like the other tabs of the theme.
RIBBON_STYLESHEET = """
QTabWidget::pane {
    border: none;
    background: palette(window);
    margin: 0px;
}
QTabWidget::tab-bar {
    alignment: left;
}
"""

GROUP_FRAME_STYLE = """
QFrame#ribbonGroup {
    border: none;
    background: transparent;
    margin: 0px;
    padding: 0px 2px;
}
"""

# No color: titles use the theme's label color, like the button labels
GROUP_TITLE_STYLE = "font-size: 9px; padding: 0px; margin-top: 1px;"
