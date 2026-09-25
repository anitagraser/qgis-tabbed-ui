# -*- coding: utf-8 -*-
"""Looking up QGIS actions by the entry names used in the tab modules."""

import re

from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMenu


def action_key(action):
    """Stable identity for an action (Python wrappers may be recreated)."""
    return sip.unwrapinstance(action)


def clean_text(text):
    """Text without mnemonic ampersands and HTML tags."""
    return re.sub(r"<[^>]+>", "", (text or "").replace("&", "")).strip()


class ActionResolver:
    """Resolves entry names (see tabs/__init__.py) to the actions of the
    QGIS main window."""

    def __init__(self, main_window, menu_parent):
        self.main_window = main_window
        # Parent of the popup menus created for ("Label", [entries]) entries,
        # so they live as long as the buttons showing them
        self.menu_parent = menu_parent
        # action key -> entry name for actions without an objectName
        self._entry_names = {}

    def entry_name(self, action):
        """The name an action is listed under in SHORT_LABELS / ICON_ONLY /
        ICON_OVERRIDES."""
        # Submenu actions usually have no objectName; use the menu's instead
        return (
            self._entry_names.get(action_key(action))
            or action.objectName()
            or (action.menu().objectName() if action.menu() is not None else "")
        )

    def resolve(self, names, placed_ids):
        """Look up actions by entry name and mark them, and the contents of
        their submenus, as placed. Missing names are skipped."""
        actions = []

        def add(action):
            actions.append(action)
            placed_ids.add(action_key(action))
            if action.menu() is not None:
                placed_ids.update(action_key(a) for a in action.menu().actions())

        for name in names:
            if isinstance(name, tuple):
                label, entries = name
                entry_actions = self.resolve(entries, placed_ids)
                if entry_actions:
                    menu = QMenu(label, self.menu_parent)
                    icons = [a.icon() for a in entry_actions if not a.icon().isNull()]
                    if icons:
                        menu.setIcon(icons[0])
                    menu.addActions(entry_actions)
                    add(menu.menuAction())
                continue
            if name.startswith("dock:"):
                dock = self.main_window.findChild(QDockWidget, name[len("dock:") :])
                if dock is not None:
                    action = self.dock_action(dock)
                    # Toggle actions have no objectName; remember the entry name
                    self._entry_names[action_key(action)] = name
                    add(action)
                continue
            expand = name.endswith("/*")
            name = name.removesuffix("/*")
            if ">" in name:
                parent_name, title = name.split(">", 1)
                menu = self.find_submenu(parent_name, title)
            else:
                menu = self.main_window.findChild(QMenu, name)
            if menu is not None:
                placed_ids.add(action_key(menu.menuAction()))
                if expand:
                    for a in menu.actions():
                        if not a.isSeparator() and action_key(a) not in placed_ids:
                            add(a)
                else:
                    if ">" in name:
                        # Submenus often have no objectName; remember the
                        # entry name
                        self._entry_names[action_key(menu.menuAction())] = name
                    add(menu.menuAction())
                continue
            action = self.main_window.findChild(QAction, name)
            if action is not None:
                add(action)
        return actions

    def dock_action(self, dock):
        """A show/hide action for a panel. Unlike the dock's own
        toggleViewAction, it brings a panel tabbed behind another to the
        front instead of hiding it."""
        toggle = dock.toggleViewAction()
        action = QAction(toggle.icon(), toggle.text(), self.menu_parent)
        action.setToolTip(toggle.toolTip())
        action.setCheckable(True)
        action.setChecked(dock.isVisible())

        def show_or_hide():
            # A panel tabbed behind another is not visible, but not hidden
            if dock.isVisible():
                dock.hide()
            else:
                dock.show()
                dock.raise_()
            action.setChecked(dock.isVisible())

        action.triggered.connect(show_or_hide)
        dock.visibilityChanged.connect(action.setChecked)
        return action

    def find_submenu(self, parent_name, title):
        """Find a submenu of a named menu by its (cleaned) title."""
        parent = self.main_window.findChild(QMenu, parent_name)
        if parent is None:
            return None
        for action in parent.actions():
            if action.menu() and clean_text(action.text()) == title:
                return action.menu()
        return None
