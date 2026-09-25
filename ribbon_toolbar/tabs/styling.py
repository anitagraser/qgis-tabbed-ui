# -*- coding: utf-8 -*-
"""Styling tab: layer styling, the Labels and Annotations toolbars and
point symbol tools."""

# Hand-arranged groups added before the toolbar groups
LEADING_GROUPS = [
    ("Layer Styling", ["dock:LayerStyling"], []),
]

# Toolbar groups: (toolbar objectName, group title)
TOOLBARS = [
    ("mLabelToolBar", "Labels"),
    ("mAnnotationsToolBar", "Annotations"),
]

# Extra entries appended to toolbar groups
TOOLBAR_EXTRA_ENTRIES = {
    "mAnnotationsToolBar": ["mEditMenu>Add Annotation"],
}

# Hand-arranged groups added after the toolbar groups
GROUPS = [
    (
        "Point Symbols",
        [],
        ["mActionRotatePointSymbols", "mActionOffsetPointSymbol"],
        {"rows": 2, "icon_size": 24},
    ),
]

TOOLBAR_GROUP_OPTIONS = {
    "mLabelToolBar": {"rows": 2, "icon_size": 24, "labels": False},
    "mAnnotationsToolBar": {"rows": 2, "icon_size": 24, "labels": False},
}

ICON_OVERRIDES = {
    # The icon of QGIS' own Layer Styling button
    "dock:LayerStyling": ":/images/themes/default/propertyicons/symbology.svg",
}
