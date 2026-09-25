# -*- coding: utf-8 -*-
"""Plugins tab: the Plugins toolbar and the toolbars of third-party
plugins."""

EXTRA_TAB_GROUPS = {
    "mPluginMenu": [("Manage Plugins", ["mActionManagePlugins"], [])],
}

MENU_GROUP_REPLACEMENTS = {
    # No menu group; plugin menus are in the hamburger menu
    "mPluginMenu": [],
}

TOOLBAR_GROUP_OPTIONS = {
    "mPluginToolBar": {"rows": 2, "icon_size": 24},
}

# Split group options for the toolbars of third-party plugins
PLUGIN_TOOLBAR_OPTIONS = {"rows": 2, "icon_size": 24}

SHORT_LABELS = {
    "mActionManagePlugins": "Plugin Manager",
}
