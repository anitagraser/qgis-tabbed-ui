# -*- coding: utf-8 -*-
"""Raster tab: the Raster menu and toolbar."""

from .spec import MenuTab

TAB = MenuTab(
    menu="mRasterMenu",
    leading_groups=[
        ("Georeferencer", ["mActionShowGeoreferencer"], []),
        ("Raster Calculator", ["mActionShowRasterCalculator"], []),
    ],
)

TOOLBAR_GROUP_OPTIONS = {
    # Two rows keep the local/full and increase/decrease pairs together
    "mRasterToolBar": {"rows": 2, "icon_size": 24, "labels": False},
}

LABELED_ACTIONS = {
    "mProcessingUserMenu_native:alignrasters",
}
