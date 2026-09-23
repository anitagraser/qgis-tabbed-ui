# -*- coding: utf-8 -*-
"""Tab descriptions: each tab module defines TAB as one of these. Groups
are hand-arranged groups as described in tabs/__init__.py."""

from dataclasses import dataclass, field


# eq=False: specs are compared (and hashed) by identity
@dataclass(eq=False)
class ArrangedTab:
    """A tab of hand-arranged groups taking its actions from a QGIS menu.

    Several tabs can share a menu (e.g. Home and View): their groups are
    resolved together, so an action is placed only once, and actions of
    the menu or its toolbars (MENU_TOOLBAR_MAP) not placed on any of them
    go into a "More" group on the first one.
    """

    menu: str
    groups: list
    # Entries left out of the "More" group
    excluded: list = field(default_factory=list)
    # None: the menu title
    title: str = None
    # Shown when the ribbon is created
    default: bool = False


@dataclass(eq=False)
class MenuTab:
    """A tab showing, for each of its menus, a group per related toolbar
    (MENU_TOOLBAR_MAP) followed by a "<Menu> Menu" group of the menu actions
    not on those toolbars."""

    menu: str
    # Menus whose groups come first (they get no tab of their own)
    merged_menus: list = field(default_factory=list)
    # Groups placed at the start of the tab; their actions are left out of
    # the menu groups
    leading_groups: list = field(default_factory=list)
    # menu objectName -> groups replacing its "<Menu> Menu" group
    menu_groups: dict = field(default_factory=dict)
    # Split group options for third-party plugin toolbars, shown after the
    # menu's toolbar groups; None: not shown
    plugin_toolbar_options: dict = None
    # None: the menu title
    title: str = None
    default: bool = False


@dataclass(eq=False)
class ToolbarTab:
    """A tab of toolbar groups (laid out as split groups with their
    TOOLBAR_GROUP_OPTIONS), between hand-arranged groups."""

    title: str
    # [(toolbar objectName, group title; None: the toolbar title)]
    toolbars: list
    leading_groups: list = field(default_factory=list)
    trailing_groups: list = field(default_factory=list)
    # toolbar objectName -> entries appended to its group
    toolbar_extra_entries: dict = field(default_factory=dict)
    default: bool = False
