# -*- coding: utf-8 -*-
"""Project tab: hand-arranged groups for the Project menu."""

from .spec import ArrangedTab

GROUPS = [
    ("New", ["mActionNewProject"], []),
    ("Open", ["mActionOpenProject"], []),
    (
        "Save",
        ["mActionSaveProject"],
        ["mActionSaveProjectAs", "mActionRevertProject"],
    ),
    (
        "Project Settings",
        ["mActionProjectProperties"],
        ["mActionSnappingOptions", "mActionStyleManager", "mProjectMenu>Models"],
    ),
    (
        "Layouts",
        ["mActionNewPrintLayout"],
        ["mActionNewReport", "mActionShowLayoutManager"],
    ),
    (
        "Import/Export",
        [],
        [
            "mActionSaveMapAsImage",
            "mActionSaveMapAsPdf",
            ("DWG/DXF", ["mActionDxfExport", "mActionDwgImport"]),
            "menuImport_Export/*",
        ],
    ),
]

# mProjectFromTemplateMenu, mRecentProjectsMenu and mProjectToStorageMenu
# are the New, Open and Save buttons' dropdowns
EXCLUDED = [
    "mProjectFromTemplateMenu",
    "mActionCloseProject",
    "mActionExit",
    "mProjectFromStorageMenu",
    "mRecentProjectsMenu",
    "mProjectToStorageMenu",
    "mLayoutsMenu",
]

TAB = ArrangedTab(menu="mProjectMenu", groups=GROUPS, excluded=EXCLUDED)

ICON_OVERRIDES = {
    "mActionSnappingOptions": ":/images/themes/default/mIconSnapping.svg",
    "mProjectMenu>Models": ":/images/themes/default/processingModel.svg",
}

BUTTON_MENUS = {
    "mActionNewProject": "mProjectFromTemplateMenu",
    "mActionOpenProject": "mRecentProjectsMenu",
    "mActionSaveProject": "mProjectToStorageMenu",
}
