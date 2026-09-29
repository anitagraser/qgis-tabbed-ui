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
    # Also on the Styling tab: the most common change, one click from Home
    ("Style", ["dock:LayerStyling"], []),
    (
        "Identify",
        ["mActionIdentify"],
        ["mActionMapTips", "ActionFeatureAction", "mViewMenu>Measure"],
    ),
    ("Pan", ["mActionPan"], []),
    (
        "Zoom",
        ["mActionZoomIn", "mActionZoomOut"],
        # Filled column by column: Zoom Last and Zoom Next share the bottom row
        [
            "mActionZoomFullExtent",
            "mActionZoomLast",
            "mActionZoomToSelected",
            "mActionZoomNext",
        ],
        {"rows": 2, "icon_size": 24},
    ),
    SELECTION_GROUP,
    (
        "Data",
        ["ActionOpenTable"],
        ["mActionOpenFieldCalc", "mActionStatisticalSummary", "mMenuFilterTable"],
    ),
    # Also on the View, Raster and Vector tabs
    ("Processing", ["toolboxAction"], []),
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
    # In the dropdown of the Pan button (BUTTON_MENUS)
    "mActionPanToSelected",
    # In the dropdown of the Zoom Full button (BUTTON_MENUS)
    "mActionZoomToLayers",
    "mActionZoomActualSize",
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
    "ActionOpenTable": "Attribute Table",
    "mActionOpenFieldCalc": "Field Calculator",
    "mActionStatisticalSummary": "Statistics",
    # The Processing Toolbox, on the Home, View, Raster and Vector tabs
    "toolboxAction": "Analysis",
}

ICON_OVERRIDES = {
    # The icon of QGIS' own Measure Line tool
    "mViewMenu>Measure": ":/images/themes/default/mActionMeasure.svg",
    # The icon of the attribute table's own filter button
    "mMenuFilterTable": ":/images/themes/default/mActionFilter2.svg",
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
    "mActionZoomFullExtent": [
        "mActionZoomToLayers",
        "mActionZoomActualSize",
    ],
    "mActionPan": [
        ("mActionPanToSelected", "Pan to Selection"),
    ],
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
