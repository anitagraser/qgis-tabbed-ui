# -*- coding: utf-8 -*-
"""
Ribbon tab configuration: one module per tab, merged here into the tables
the ribbon widget reads.

Groups are (title, large buttons, small buttons), LibreOffice style.
Entries are QAction or QMenu objectNames, or "menuName>Submenu Title" for
submenus without an objectName; a menu entry becomes a popup button,
"name/*" expands a menu into its individual actions (those not placed yet),
a ("Label", [entries]) tuple becomes a popup button with those entries,
and "dock:objectName" is the show/hide action of that panel. Missing names
are skipped. An optional 4th element holds layout options for the small
buttons: {"rows": number of rows (default 3), "icon_size": icon size in px,
"labels": False to show small buttons compactly (icon only if they have an
icon, otherwise text only)}.

Each tab module may define any of these tables, which are merged:

ARRANGED_TABS: menu objectName -> (excluded entries, [(tab title, groups),
    ...]). A menu can be split over several tabs; a tab title of None uses
    the menu title, and actions from the menu / its toolbars not arranged
    go into a "More" group on the first tab.
EXTRA_TAB_GROUPS: menu objectName -> groups placed at the start of that
    standard (not arranged) tab, e.g. for actions from other menus.
MERGED_TABS: standard tab menu -> other menus whose groups it also shows
    (they then get no tab of their own), before the tab's own groups.
MENU_GROUP_REPLACEMENTS: menu objectName -> groups replacing its menu
    group ("<Menu> Menu").
TOOLBAR_GROUP_OPTIONS: toolbar objectName -> options laying out its group
    as a split group of small buttons; "large" lists the objectNames of
    actions shown as large buttons instead, "only" limits the group to the
    listed objectNames, "exclude" leaves the listed ones out.
TOOLBAR_TABS: [(tab title, [toolbar objectNames])] for tabs (before the
    Styling tab) showing one group per toolbar.
SHORT_LABELS: entry name -> shorter button label (tooltips keep the full
    text).
ICON_OVERRIDES: entry name -> icon for buttons whose action has none: a
    file in the plugin's icons folder, or a Qt resource path (":/...").
ICON_ONLY: entry names shown without a label (tooltips keep the text).
BUTTON_MENUS: action objectName -> dropdown for its button (click runs the
    action, the arrow shows the listed (action objectName, label) entries,
    or the QMenu with the given objectName).
LABELED_ACTIONS: actions whose small buttons on standard tabs show their
    label beside the icon (instead of the icon only).
"""

from . import gps, home, mesh, plugins, project, raster, styling, vector, view

TAB_MODULES = [project, home, view, raster, vector, mesh, gps, styling, plugins]

# Menu tabs, in the order they appear in the ribbon
TAB_ORDER = [
    "mProjectMenu",
    "mViewMenu",
    "mRasterMenu",
    "mVectorMenu",
    "mMeshMenu",
]

# Menu tabs placed after TOOLBAR_TABS and the Styling tab
TRAILING_TAB_ORDER = [
    "mPluginMenu",
]

# Tab shown when the ribbon is created
DEFAULT_TAB = "mViewMenu"


def _merge(name, kind=dict, modules=TAB_MODULES):
    """Merge the table `name` of all tab modules. Dict keys must be unique,
    so one tab cannot silently override another's entry."""
    merged = kind()
    for module in modules:
        table = getattr(module, name, kind())
        if kind is dict:
            duplicates = merged.keys() & table.keys()
            if duplicates:
                raise ValueError(
                    f"{module.__name__}.{name} redefines {sorted(duplicates)}"
                )
        merged.update(table)
    return merged


ARRANGED_TABS = _merge("ARRANGED_TABS")
# The View menu is split over the Home and View tabs
ARRANGED_TABS["mViewMenu"] = (
    home.EXCLUDED + view.EXCLUDED,
    [("Home", home.GROUPS), ("View", view.GROUPS)],
)
EXTRA_TAB_GROUPS = _merge("EXTRA_TAB_GROUPS")
MERGED_TABS = _merge("MERGED_TABS")
MENU_GROUP_REPLACEMENTS = _merge("MENU_GROUP_REPLACEMENTS")
TOOLBAR_GROUP_OPTIONS = _merge("TOOLBAR_GROUP_OPTIONS")
TOOLBAR_TABS = [tab for module in TAB_MODULES for tab in getattr(module, "TOOLBAR_TABS", [])]
SHORT_LABELS = _merge("SHORT_LABELS")
ICON_OVERRIDES = _merge("ICON_OVERRIDES")
ICON_ONLY = _merge("ICON_ONLY", set)
BUTTON_MENUS = _merge("BUTTON_MENUS")
LABELED_ACTIONS = _merge("LABELED_ACTIONS", set)
