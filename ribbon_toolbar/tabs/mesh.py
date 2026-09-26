# -*- coding: utf-8 -*-
"""Mesh tab: the Mesh menu and toolbar."""

from .spec import MenuTab

TAB = MenuTab(
    menu="mMeshMenu",
    leading_groups=[("Mesh Calculator", ["mActionShowMeshCalculator"], [])],
)

TOOLBAR_GROUP_OPTIONS = {
    "mMeshToolBar": {"rows": 2, "icon_size": 24},
}

ICON_OVERRIDES = {
    # QGIS ships this icon but does not set it on the action
    "mActionShowMeshCalculator": ":/images/themes/default/mActionShowMeshCalculator.svg",
}

LABELED_ACTIONS = {
    "mActionReindexMesh",
}
