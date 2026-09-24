# -*- coding: utf-8 -*-
"""Styling tab: layer styling, the Labels and Annotations toolbars and
point symbol tools."""

from .spec import ToolbarTab

TAB = ToolbarTab(
    title="Styling",
    leading_groups=[("Layer Styling", ["dock:LayerStyling"], [])],
    toolbars=[
        ("mLabelToolBar", "Labels"),
        ("mAnnotationsToolBar", "Annotations"),
    ],
    toolbar_extra_entries={
        "mAnnotationsToolBar": ["mActionHtmlAnnotation"],
    },
    trailing_groups=[
        (
            "Point Symbols",
            [],
            ["mActionRotatePointSymbols", "mActionOffsetPointSymbol"],
            {"rows": 2, "icon_size": 24},
        ),
    ],
)

TOOLBAR_GROUP_OPTIONS = {
    "mLabelToolBar": {"rows": 2, "icon_size": 24, "labels": False},
    "mAnnotationsToolBar": {"rows": 2, "icon_size": 24, "labels": False},
}

ICON_OVERRIDES = {
    # The icon of QGIS' own Layer Styling button
    "dock:LayerStyling": ":/images/themes/default/propertyicons/symbology.svg",
}
