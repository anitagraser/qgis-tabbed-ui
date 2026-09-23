# -*- coding: utf-8 -*-
"""View tab: hand-arranged groups from the View menu (built together with
the Home tab, see tabs/__init__.py)."""

GROUPS = [
    ("Map Views", ["mActionNewMapCanvas"], ["mViewMenu>3D Map Views", "mActionDraw"]),
    (
        "Display",
        [],
        [
            "mActionTemporalController",
            "mActionElevationController",
            "mViewMenu>Elevation Profiles",
            "mViewMenu>Decorations",
            "mViewMenu>Preview Mode",
        ],
    ),
    (
        "Overview",
        ["dock:Overview"],
        [
            "mActionAddToOverview",
            "mActionAddAllToOverview",
            "mActionRemoveAllFromOverview",
        ],
    ),
    ("Processing", ["toolboxAction"], []),
]

EXCLUDED = [
    "mViewMenu>Panels",
    "mViewMenu>Toolbars",
    "mViewMenu>Layer Visibility",
    # Its actions are shown individually in the Display group
    "mViewMenu>Data Filtering",
    "mActionToggleFullScreen",
    "mActionTogglePanelsVisibility",
    "mActionToggleMapOnly",
    "mActionShowBookmarks",
]

SHORT_LABELS = {
    "dock:Overview": "Show Overview",
}

ICON_OVERRIDES = {
    "dock:Overview": "overview.svg",
}
