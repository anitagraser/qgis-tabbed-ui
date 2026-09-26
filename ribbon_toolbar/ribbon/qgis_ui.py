# -*- coding: utf-8 -*-
"""QGIS' own menus and toolbars: how they relate, and collecting them from
the main window."""

from qgis.PyQt.QtWidgets import QMenu, QToolBar

# Mapping: menu objectName -> list of related toolbar objectNames
MENU_TOOLBAR_MAP = {
    "mProjectMenu": ["mFileToolBar"],
    "mEditMenu": [
        "mDigitizeToolBar",
        "mAdvancedDigitizeToolBar",
        "mShapeDigitizeToolBar",
    ],
    "mViewMenu": ["mMapNavToolBar", "mAttributesToolBar"],
    "mLayerMenu": ["mLayerToolBar", "mDataSourceManagerToolBar"],
    "mSettingsMenu": [],
    "mPluginMenu": ["mPluginToolBar"],
    "mRasterMenu": ["mRasterToolBar"],
    "mVectorMenu": ["mVectorToolBar"],
    "processing": ["processingToolbar"],
    "mMeshMenu": ["mMeshToolBar"],
    "mDatabaseMenu": ["mDatabaseToolBar"],
    "mWebMenu": ["mWebToolBar"],
    "mHelpMenu": ["mHelpToolBar"],
}

# QGIS toolbars not related to a menu (so not from third-party plugins)
KNOWN_INTERNAL_TOOLBARS = {
    "mSnappingToolBar",
    "mLabelToolBar",
    "mAnnotationsToolBar",
    "mGpsToolBar",
    "mBookmarkToolbar",
    "mBrowserToolbar",
    "mSelectionToolBar",
    "mToolbar",
    # The toolbar hosting the ribbon (RibbonToolbarPlugin.RIBBON_OBJECT_NAME)
    "RibbonToolbarMain",
}

# Submenus shown as popup buttons in "<Menu> Menu" groups:
# (menu objectName, submenu title)
MENU_POPUP_ACTIONS = {
    ("mRasterMenu", "Analysis"),
    ("mRasterMenu", "Projections"),
    ("mRasterMenu", "Miscellaneous"),
    ("mRasterMenu", "Extraction"),
    ("mRasterMenu", "Conversion"),
}


def collect_toolbars(main_window):
    """All named toolbars of the main window, by objectName."""
    return {
        tb.objectName(): tb
        for tb in main_window.findChildren(QToolBar)
        if tb.objectName()
    }


def collect_menus(menubar):
    """The menubar's top-level menus, by objectName."""
    return {
        menu.objectName(): menu
        for menu in menubar.findChildren(QMenu)
        if menu.parent() == menubar
    }


def is_plugin_toolbar(name):
    """Whether a toolbar comes from a third-party plugin (is neither related
    to a menu nor a known QGIS toolbar)."""
    return not any(
        name in toolbars for toolbars in MENU_TOOLBAR_MAP.values()
    ) and name not in KNOWN_INTERNAL_TOOLBARS
