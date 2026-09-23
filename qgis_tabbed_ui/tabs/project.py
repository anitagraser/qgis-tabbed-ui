# -*- coding: utf-8 -*-
"""Project tab: hand-arranged groups for the Project menu."""

GROUPS = [
    ("New", ["mActionNewProject"], ["mProjectFromTemplateMenu", "mActionCloseProject"]),
    ("Open", ["mActionOpenProject"], []),
    (
        "Save",
        ["mActionSaveProject"],
        ["mActionSaveProjectAs", "mProjectToStorageMenu", "mActionRevertProject"],
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
            ("Export Map to…", ["mActionSaveMapAsImage", "mActionSaveMapAsPdf"]),
            ("DWG/DXF", ["mActionDxfExport", "mActionDwgImport"]),
            "menuImport_Export/*",
        ],
    ),
]

# mRecentProjectsMenu is the Open button's dropdown
EXCLUDED = [
    "mActionExit",
    "mProjectFromStorageMenu",
    "mRecentProjectsMenu",
    "mLayoutsMenu",
]

ARRANGED_TABS = {
    "mProjectMenu": (EXCLUDED, [(None, GROUPS)]),
}

SHORT_LABELS = {
    "mProjectFromTemplateMenu": "From Template",
}

BUTTON_MENUS = {
    "mActionOpenProject": "mRecentProjectsMenu",
}
