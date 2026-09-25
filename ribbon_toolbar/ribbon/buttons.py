# -*- coding: utf-8 -*-
"""Ribbon buttons: tool buttons for QGIS actions, clones of QGIS' own tool
buttons, and the per-entry label and icon overrides."""

from pathlib import Path

from qgis.PyQt import sip
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QAction,
    QMenu,
    QSizePolicy,
    QToolButton,
    QWidgetAction,
)

from ..tabs import (
    BUTTON_MENUS,
    ICON_ONLY,
    ICON_OVERRIDES,
    LABELED_ACTIONS,
    SHORT_LABELS,
)
from .actions import clean_text
from .qgis_ui import MENU_POPUP_ACTIONS
from .styles import (
    LARGE_BUTTON_HEIGHT,
    LARGE_BUTTON_WIDTH,
    LARGE_ICON_SIZE,
    SMALL_BUTTON_HEIGHT,
    SMALL_ICON_SIZE,
)

ICONS_DIR = Path(__file__).parent.parent / "icons"


def style_button(btn, large, labeled, has_icon):
    """Set a ribbon button's size and label style. Large buttons show the
    label under the icon; small ones beside it if labeled, otherwise the
    icon only (or the text only if there is no icon)."""
    if large:
        btn.setIconSize(QSize(LARGE_ICON_SIZE, LARGE_ICON_SIZE))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        if labeled:
            btn.setFixedHeight(LARGE_BUTTON_HEIGHT)
            btn.setMinimumWidth(LARGE_BUTTON_WIDTH)
        else:
            btn.setFixedSize(LARGE_BUTTON_WIDTH, LARGE_BUTTON_HEIGHT)
        return
    btn.setIconSize(QSize(SMALL_ICON_SIZE, SMALL_ICON_SIZE))
    if labeled:
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    elif has_icon:
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    else:
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
    btn.setFixedHeight(SMALL_BUTTON_HEIGHT)


def clone_widget_button(source, large=False, parent=None, popup=False, labeled=False):
    """Clone a QToolButton from a QWidgetAction's defaultWidget.
    Returns None for non-QToolButton widgets (spinboxes, etc.).
    popup/labeled: as for ButtonFactory.make_button."""
    if not isinstance(source, QToolButton):
        return None
    clone = QToolButton(parent)
    clone.setIcon(source.icon())
    clone.setToolTip(source.toolTip())
    clone.setAutoRaise(True)
    if popup:
        clone.setMenu(source.menu())
        clone.setPopupMode(source.popupMode())
    # Wire click through to the hidden original so all internal logic fires
    clone.clicked.connect(source.click)
    if labeled:
        default_action = source.defaultAction()
        clone.setText(
            clean_text(default_action.text() if default_action else "")
            or clean_text(source.toolTip())
        )
    style_button(clone, large, labeled, not source.icon().isNull())
    return clone


def _sync_menu_button(button, action):
    """Keep a popup-only menu button aligned with its source action."""
    if sip.isdeleted(button):
        return
    button.setText(clean_text(action.text()))
    button.setIcon(action.icon())
    button.setToolTip(clean_text(action.toolTip()) or clean_text(action.text()))
    button.setStatusTip(action.statusTip())
    button.setEnabled(action.isEnabled())
    button.setVisible(action.isVisible())


def _sync_popup_menu(popup_menu, source_menu):
    """Mirror the current actions from a source menu into a detached popup."""
    popup_menu.clear()
    popup_menu.addActions(source_menu.actions())


class ButtonFactory:
    """Creates the buttons of ribbon groups."""

    def __init__(self, main_window, resolver):
        self.main_window = main_window
        self.resolver = resolver

    def make_button(
        self,
        action,
        large=False,
        menu_name=None,
        parent=None,
        popup=None,
        labeled=False,
    ):
        """Create a QToolButton for a ribbon action.

        popup: show the action's submenu as a popup (default: looked up in
        MENU_POPUP_ACTIONS for menu_name). labeled: always show the full
        label (small buttons get text beside the icon, large ones grow in
        width).
        """
        btn = QToolButton(parent)
        btn.setAutoRaise(True)

        if popup is None:
            popup = (
                menu_name,
                action.objectName() or clean_text(action.text()),
            ) in MENU_POPUP_ACTIONS
        if popup:
            source_menu = action.menu()
            _sync_menu_button(btn, action)
            popup_menu = QMenu(btn)
            _sync_popup_menu(popup_menu, source_menu)
            popup_menu.aboutToShow.connect(
                lambda popup_menu=popup_menu, action=action: _sync_popup_menu(
                    popup_menu, action.menu()
                )
            )
            btn.setMenu(popup_menu)
            btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            action.changed.connect(
                lambda btn=btn, action=action: _sync_menu_button(btn, action)
            )
        else:
            btn.setDefaultAction(action)
            entries = BUTTON_MENUS.get(action.objectName())
            if isinstance(entries, str):
                # Show an existing QGIS menu (kept up to date by QGIS)
                button_menu = self.main_window.findChild(QMenu, entries)
            elif entries:
                button_menu = self._make_button_menu(entries, btn)
            else:
                button_menu = None
            if button_menu is not None:
                btn.setMenu(button_menu)
                btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        has_icon = not action.icon().isNull()
        if not large:
            labeled = labeled or action.objectName() in LABELED_ACTIONS
        style_button(btn, large, labeled, has_icon)
        if not large:
            if labeled and not has_icon:
                # Blank icon keeps labels aligned with iconed buttons
                blank = QPixmap(SMALL_ICON_SIZE, SMALL_ICON_SIZE)
                blank.fill(Qt.GlobalColor.transparent)
                btn.setIcon(QIcon(blank))
            elif not labeled and not has_icon:
                btn.setMaximumWidth(120)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        return btn

    def _make_button_menu(self, entries, parent):
        """Build a dropdown for BUTTON_MENUS entries: QGIS' own actions, or
        relabelled proxies for (objectName, label) entries."""
        menu = QMenu(parent)
        for entry in entries:
            name, label = entry if isinstance(entry, tuple) else (entry, None)
            source = self.main_window.findChild(QAction, name)
            if source is None:
                continue
            if label is None:
                # Shares its enabled and checked state with QGIS
                menu.addAction(source)
                continue
            proxy = menu.addAction(source.icon(), label)
            proxy.triggered.connect(source.trigger)

            def sync(proxy=proxy, source=source):
                if not sip.isdeleted(proxy):
                    proxy.setEnabled(source.isEnabled())

            sync()
            source.changed.connect(sync)
        return menu

    def make_small_button(self, action, menu_name=None, parent=None):
        """Create a small button for a plain group; None if unsupported."""
        if isinstance(action, QWidgetAction):
            return clone_widget_button(action.defaultWidget(), parent=parent)
        return self.make_button(action, menu_name=menu_name, parent=parent)

    def make_arranged_button(self, action, large, parent, labeled=True):
        """Create a labelled button for a split group, applying SHORT_LABELS,
        ICON_OVERRIDES and ICON_ONLY; None if unsupported."""
        if isinstance(action, QWidgetAction):
            source = action.defaultWidget()
            if not isinstance(source, QToolButton):
                return None
            btn = clone_widget_button(
                source,
                large=large,
                parent=parent,
                popup=source.menu() is not None,
                labeled=labeled,
            )
        else:
            btn = self.make_button(
                action,
                large=large,
                popup=action.menu() is not None,
                labeled=labeled,
                parent=parent,
            )

        name = self.resolver.entry_name(action)
        short_label = SHORT_LABELS.get(name)
        icon_file = ICON_OVERRIDES.get(name)
        icon = None
        if icon_file:
            if not icon_file.startswith(":"):
                icon_file = str(ICONS_DIR / icon_file)
            icon = QIcon(icon_file)
        if short_label or icon:

            def apply_overrides(btn=btn, label=short_label, icon=icon):
                if sip.isdeleted(btn):
                    return
                if label:
                    btn.setText(label)
                if icon:
                    btn.setIcon(icon)

            apply_overrides()
            # The button resets its text and icon from the action on every
            # change (e.g. when checked or enabled), so reapply afterwards
            action.changed.connect(apply_overrides)

        # Actions without an icon keep their label even when listed
        if name in ICON_ONLY and (icon or not action.icon().isNull()):
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            btn.setMinimumWidth(0)
        # Never shrink below the label width (Qt would elide the text)
        if labeled:
            btn.setMinimumWidth(max(btn.minimumWidth(), btn.sizeHint().width()))
        return btn
