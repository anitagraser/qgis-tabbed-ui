# -*- coding: utf-8 -*-
"""Vector tab: the Edit menu and digitizing toolbars, followed by the
Vector menu and toolbar."""

from .home import SELECTION_GROUP

MERGED_TABS = {
    "mVectorMenu": ["mEditMenu"],
}

EXTRA_TAB_GROUPS = {
    # The Edit menu's groups come first on the Vector tab (MERGED_TABS)
    "mEditMenu": [
        (
            "Layer",
            [],
            ["mNewLayerMenu", "mActionToggleEditing", "EnableSnappingAction"],
        )
    ],
}

# The Edit and Vector menus are not shown as menu groups
MENU_GROUP_REPLACEMENTS = {
    "mEditMenu": [SELECTION_GROUP],
    "mVectorMenu": [("Processing", ["toolboxAction"], [])],
}

TOOLBAR_GROUP_OPTIONS = {
    "mAdvancedDigitizeToolBar": {"rows": 2, "icon_size": 24, "labels": False},
    "mShapeDigitizeToolBar": {"rows": 2, "icon_size": 24, "labels": False},
    "mDigitizeToolBar": {
        "rows": 2,
        "icon_size": 24,
        "labels": False,
        "large": ["mActionAddFeature", "ActionVertexTool"],
        # Shown in the tab's first group instead
        "exclude": ["mActionToggleEditing"],
    },
}

SHORT_LABELS = {
    "mActionToggleEditing": "Toggle Editing",
    "EnableSnappingAction": "Enable Snapping",
    "ActionVertexTool": "Vertex Tool",
    "mActionAddFeature": "Add Feature",
}

BUTTON_MENUS = {
    "mActionPasteFeatures": [
        ("mActionPasteAsNewVector", "Paste as New Vector Layer…"),
        ("mActionPasteAsNewMemoryVector", "Paste as New Scratch Layer…"),
    ],
    "EnableSnappingAction": [("mActionSnappingOptions", "Snapping Options…")],
}
