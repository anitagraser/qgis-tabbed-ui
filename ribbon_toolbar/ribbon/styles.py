# -*- coding: utf-8 -*-
"""Stylesheets and sizes of the ribbon."""

# Button sizes (px)
LARGE_ICON_SIZE = 28
LARGE_BUTTON_WIDTH = 56
LARGE_BUTTON_HEIGHT = 70
SMALL_ICON_SIZE = 18
SMALL_BUTTON_HEIGHT = 22
# Rows of small buttons per column in a group
DEFAULT_ROWS = 3

# Colors use palette() roles so the ribbon follows the active QGIS theme
# (e.g. Night Mapping) instead of hard-coded light colors.
RIBBON_STYLESHEET = """
QTabWidget::pane {
    border: 1px solid palette(mid);
    background: palette(window);
    margin: 0px;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar::tab {
    background: palette(button);
    border: 1px solid palette(mid);
    border-bottom: none;
    padding: 5px 14px;
    margin-right: 1px;
    font-weight: 500;
    min-width: 50px;
    color: palette(button-text);
}
QTabBar::tab:selected {
    background: palette(window);
    border-top: 2px solid palette(highlight);
    border-bottom: 1px solid palette(window);
    color: palette(window-text);
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    background: palette(midlight);
}
"""

GROUP_FRAME_STYLE = """
QFrame#ribbonGroup {
    border-right: 1px solid palette(mid);
    background: transparent;
    margin: 0px;
    padding: 0px 2px;
}
"""

GROUP_TITLE_STYLE = (
    "color: palette(window-text); font-size: 9px; padding: 0px; margin-top: 1px;"
)
