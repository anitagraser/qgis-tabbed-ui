# -*- coding: utf-8 -*-
"""Vector tab: the Edit menu and digitizing toolbars, followed by the
Vector menu and toolbar."""

from .home import SELECTION_GROUP
from .spec import MenuTab

TAB = MenuTab(
    menu="mVectorMenu",
    merged_menus=["mEditMenu"],
    leading_groups=[
        (
            "Layer",
            [],
            ["mNewLayerMenu", "mActionToggleEditing", "EnableSnappingAction"],
        )
    ],
    # The Edit and Vector menus are not shown as menu groups
    menu_groups={
        "mEditMenu": [SELECTION_GROUP],
        "mVectorMenu": [("Processing", ["toolboxAction"], [])],
    },
)

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
