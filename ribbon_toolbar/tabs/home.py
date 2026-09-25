# -*- coding: utf-8 -*-
"""Home tab: hand-arranged groups from the View and Layer menus (resolved
together with the View tab, which shares the View menu)."""

from .spec import ArrangedTab

# Shared by the Home and Vector tabs
SELECTION_GROUP = (
    "Selection",
    ["mActionSelectFeatures"],
    [
        "mActionSelectByForm",
        "mActionSelectByExpression",
        "mActionInvertSelection",
        "mActionDeselectActiveLayer",
    ],
    {"rows": 2, "icon_size": 24},
)

GROUPS = [
    ("Layer", ["mActionDataSourceManager"], ["mLayerMenu/*"], {"labels": False}),
    (
        "Identify",
        ["mActionIdentify"],
        ["mActionMapTips", "ActionFeatureAction", "mViewMenu>Measure"],
    ),
    (
        "Pan",
        ["mActionPan"],
        ["mActionPanToSelected", "mActionNewBookmark", "mActionShowBookmarkManager"],
    ),
    (
        "Zoom",
        ["mActionZoomIn", "mActionZoomOut"],
        [
            "mActionZoomFullExtent",
            "mActionZoomToSelected",
            "mActionZoomToLayers",
            "mActionZoomLast",
            "mActionZoomNext",
            "mActionZoomActualSize",
        ],
        {"rows": 2, "icon_size": 24},
    ),
    SELECTION_GROUP,
    (
        "Attributes",
        ["ActionOpenTable"],
        ["mActionOpenFieldCalc", "mActionStatisticalSummary", "mMenuFilterTable"],
    ),
]

EXCLUDED = [
    # In the dropdown of the Select Features button (BUTTON_MENUS)
    "mActionSelectPolygon",
    "mActionSelectFreehand",
    "mActionSelectRadius",
    "mActionSelectAll",
    "mActionReselect",
    # In the dropdown of the Deselect button (BUTTON_MENUS)
    "mActionDeselectAll",
    # Duplicates the Measure submenu
    "ActionMeasure",
    # Layer menu actions left out of the Layer group
    # (mActionOpenTable duplicates the Attribute Table button)
    "mActionOpenTable",
    "mActionLayerSaveAs",
    "mActionSaveLayerDefinition",
    "mActionLayerProperties",
    "mActionSetLayerScaleVisibility",
    "mActionSetLayerCRS",
    "mActionSetProjectCRSFromLayer",
    "mActionLabeling",
    "mActionRemoveLayer",
    "mActionLayerSubsetString",
    "mActionDuplicateLayer",
    "mActionCopyLayer",
    "mActionPasteLayer",
    # On the Vector tab instead
    "mNewLayerMenu",
    # In the Add Layer button's dropdown
    "mActionEmbedLayers",
    "mActionAddLayerDefinition",
    # Shown on the Raster / Vector tab / Layers panel toolbar instead
    "mActionShowGeoreferencer",
    "mActionToggleEditing",
    "mActionSaveLayerEdits",
    "mActionAllEdits",
    "mActionCopyStyle",
    "mActionPasteStyle",
    "mAddLayerMenu",
]

TAB = ArrangedTab(
    menu="mViewMenu", title="Home", groups=GROUPS, excluded=EXCLUDED, default=True
)

SHORT_LABELS = {
    "mActionDataSourceManager": "Add Layer",
    "mActionIdentify": "Identify",
    "mActionPan": "Pan",
    "mActionPanToSelected": "Pan to Selection",
    "mActionNewBookmark": "New Bookmark",
    "mActionShowBookmarkManager": "Bookmark Manager",
    "ActionOpenTable": "Attribute Table",
    "mActionOpenFieldCalc": "Field Calculator",
    "mActionStatisticalSummary": "Statistics",
}

ICON_ONLY = {
    "mActionZoomIn",
    "mActionZoomOut",
    "mActionZoomFullExtent",
    "mActionZoomToSelected",
    "mActionZoomToLayers",
    "mActionZoomLast",
    "mActionZoomNext",
    "mActionZoomActualSize",
    "mActionSelectByForm",
    "mActionSelectByExpression",
    "mActionInvertSelection",
    "mActionDeselectActiveLayer",
}

BUTTON_MENUS = {
    "mActionSelectFeatures": [
        "mActionSelectPolygon",
        "mActionSelectFreehand",
        "mActionSelectRadius",
        "mActionSelectAll",
        "mActionReselect",
    ],
    "mActionDeselectActiveLayer": [
        "mActionDeselectAll",
    ],
    "mActionDataSourceManager": [
        ("mActionEmbedLayers", "Embed Layers and Groups…"),
        ("mActionAddLayerDefinition", "Add from Layer Definition File…"),
    ],
}
