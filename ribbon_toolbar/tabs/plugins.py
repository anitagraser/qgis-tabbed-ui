# -*- coding: utf-8 -*-
"""Plugins tab: the Plugins toolbar and the toolbars of third-party
plugins."""

from .spec import MenuTab

TAB = MenuTab(
    menu="mPluginMenu",
    leading_groups=[("Manage Plugins", ["mActionManagePlugins"], [])],
    # No menu group; plugin menus are in the hamburger menu
    menu_groups={"mPluginMenu": []},
    plugin_toolbar_options={"rows": 2, "icon_size": 24},
)

TOOLBAR_GROUP_OPTIONS = {
    "mPluginToolBar": {"rows": 2, "icon_size": 24},
}

SHORT_LABELS = {
    "mActionManagePlugins": "Plugin Manager",
}
