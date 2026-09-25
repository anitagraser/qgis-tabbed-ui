# -*- coding: utf-8 -*-
"""
Main plugin class for Ribbon Toolbar.
Handles plugin lifecycle and toggling between ribbon and classic UI.
"""

from pathlib import Path

from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QHBoxLayout,
    QMenu,
    QToolBar,
    QToolButton,
    QWidget,
)


class RibbonToolbarPlugin:
    """QGIS Plugin: Replaces menus/toolbars with a ribbon interface."""

    RIBBON_OBJECT_NAME = "RibbonToolbarMain"

    def __init__(self, iface):
        self.iface = iface
        self.main_window = iface.mainWindow()
        self.ribbon_active = False
        self.ribbon_toolbar = None
        self.ribbon_widget = None
        self.toggle_action = None
        self.menubar_action = None
        # Store original visibility states for toolbars
        self._original_toolbar_visibility = {}
        self._original_menubar_visible = True
        self._original_menubar_max_height = None
        self.plugin_dir = Path(__file__).parent
        # Menubar corner widget
        self._corner_widget = None
        self._corner_layout = None

    def initGui(self):
        """Called when plugin is loaded."""
        icon_path = self.plugin_dir / "icon.svg"
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

        # Toggle action
        self.toggle_action = QAction(icon, "Toggle Ribbon Toolbar", self.main_window)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)
        self.toggle_action.triggered.connect(self._on_toggle)
        self.iface.addToolBarIcon(self.toggle_action)
        self.iface.addPluginToMenu("&Ribbon Toolbar", self.toggle_action)

        # Show/hide the (collapsed) menubar while the ribbon is active
        self.menubar_action = QAction(
            QIcon(str(self.plugin_dir / "menubar.svg")),
            "Toggle Menu Bar",
            self.main_window,
        )
        self.menubar_action.setCheckable(True)
        self.menubar_action.toggled.connect(self._set_menubar_expanded)

        # Create the menubar corner widget as a proper child of the menubar so it
        # is still visible when the main window layout is finalized after startup.
        self._corner_widget = QWidget(self.main_window.menuBar())
        self._corner_widget.setObjectName("RibbonToggleCornerWidget")
        self._corner_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._corner_layout = QHBoxLayout(self._corner_widget)
        self._corner_layout.setContentsMargins(0, 0, 10, 0)
        self._corner_layout.setSpacing(0)

        toggle_button = self._make_toggle_button(self._corner_widget)
        self._corner_layout.addWidget(toggle_button)
        self._corner_widget.setVisible(True)
        self.main_window.menuBar().setCornerWidget(
            self._corner_widget, Qt.Corner.TopRightCorner
        )

        # Connect to initialization completed to render ribbon
        self.iface.initializationCompleted.connect(self._on_initialization_completed)

    def unload(self):
        """Called when plugin is unloaded."""
        if self.ribbon_active:
            self._deactivate_ribbon()
        self.iface.removePluginMenu("&Ribbon Toolbar", self.toggle_action)
        self.iface.removeToolBarIcon(self.toggle_action)
        self.menubar_action.deleteLater()
        self.menubar_action = None

        # Disconnect initialization signal if still connected
        try:
            self.iface.initializationCompleted.disconnect(
                self._on_initialization_completed
            )
        except TypeError:
            pass

        # Remove the toggle button from the menubar corner
        if self._corner_widget is not None:
            self._corner_widget.hide()
            self._corner_widget.deleteLater()
            self._corner_widget = None
        menubar = self.main_window.menuBar()
        menubar.setCornerWidget(QWidget())

    def _make_toggle_button(self, parent=None):
        """Create a tool button bound to the toggle action."""
        button = QToolButton(parent)
        button.setDefaultAction(self.toggle_action)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        return button

    def _make_quick_access_bar(self):
        """Create the row of quick access buttons left of the ribbon tabs."""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(2, 0, 6, 0)
        layout.setSpacing(0)
        actions = [
            self.menubar_action,
            self.iface.actionOpenProject(),
            self.iface.actionSaveProject(),
            self.main_window.findChild(QAction, "mActionUndo"),
            self.main_window.findChild(QAction, "mActionRedo"),
        ]
        for action in actions:
            if action is None:
                continue
            button = QToolButton(bar)
            button.setDefaultAction(action)
            button.setAutoRaise(True)
            layout.addWidget(button)
        return bar

    def _make_hamburger_button(self):
        """Create the hamburger button that gives access to all QGIS menus."""
        button = QToolButton()
        button.setIcon(QIcon(str(self.plugin_dir / "hamburger.svg")))
        button.setToolTip("Menu")
        button.setAutoRaise(True)
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        menu = QMenu(button)
        # Rebuild on each show so menus added later (e.g. by plugins) appear
        menu.aboutToShow.connect(lambda: self._populate_hamburger_menu(menu))
        button.setMenu(menu)
        return button

    def _populate_hamburger_menu(self, menu):
        menu.clear()
        for action in self.main_window.menuBar().actions():
            if action.menu() is not None and action.isVisible():
                menu.addAction(action)
        menu.addSeparator()
        menu.addAction(self.menubar_action)
        menu.addAction(self.toggle_action)

    def _set_menubar_expanded(self, expanded):
        """Expand or collapse the menubar while the ribbon is active."""
        if not self.ribbon_active:
            return
        menubar = self.main_window.menuBar()
        menubar.setMaximumHeight(
            self._original_menubar_max_height if expanded else 0
        )

    def _on_initialization_completed(self):
        """Called after QGIS initialization is complete. Activate ribbon and render UI."""
        try:
            self.iface.initializationCompleted.disconnect(
                self._on_initialization_completed
            )
        except TypeError:
            pass

        # Activate ribbon by default after initialization
        self._on_toggle(True)

    def _on_toggle(self, checked):
        if checked:
            self._activate_ribbon()
        else:
            self._deactivate_ribbon()

    def _activate_ribbon(self):
        """Hide menus/toolbars and show the ribbon."""
        if self.ribbon_active:
            return

        # Save current state
        self._original_menubar_visible = self.main_window.menuBar().isVisible()
        self._original_toolbar_visibility = {}
        for tb in self.main_window.findChildren(QToolBar):
            if (
                tb.objectName() != self.RIBBON_OBJECT_NAME
                and tb.parent() == self.main_window
            ):
                self._original_toolbar_visibility[tb.objectName()] = tb.isVisible()

        QgsMessageLog.logMessage(
            str(self._original_toolbar_visibility).replace(",", ",\n"),
            "Ribbon Toolbar",
            level=Qgis.MessageLevel.Info,
        )

        # Build the ribbon
        from .ribbon_widget import RibbonWidget

        self.ribbon_widget = RibbonWidget(self.iface, self.main_window)

        # Create the hosting toolbar
        self.ribbon_toolbar = QToolBar("Ribbon", self.main_window)
        self.ribbon_toolbar.setObjectName(self.RIBBON_OBJECT_NAME)
        self.ribbon_toolbar.setMovable(False)
        self.ribbon_toolbar.setFloatable(False)
        self.ribbon_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        self.ribbon_widget.build_ribbon()
        # LibreOffice-style corners: quick access buttons left of the tabs,
        # hamburger menu (which also holds the ribbon toggle) on the right
        self.ribbon_widget.setCornerWidget(
            self._make_quick_access_bar(), Qt.Corner.TopLeftCorner
        )
        self.ribbon_widget.setCornerWidget(
            self._make_hamburger_button(), Qt.Corner.TopRightCorner
        )
        self.ribbon_toolbar.addWidget(self.ribbon_widget)
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.ribbon_toolbar)

        # Hide toolbars docked to the main window only (not toolbars inside panels)
        for tb in self.main_window.findChildren(QToolBar):
            if (
                tb.objectName() != self.RIBBON_OBJECT_NAME
                and tb.parent() == self.main_window
            ):
                tb.setVisible(False)

        # Collapse the menubar instead of hiding it: Qt only triggers menu
        # action shortcuts while the menubar is visible
        menubar = self.main_window.menuBar()
        self._original_menubar_max_height = menubar.maximumHeight()
        menubar.setMaximumHeight(0)

        self.ribbon_active = True
        self.menubar_action.setChecked(False)

    def _deactivate_ribbon(self):
        """Restore menus/toolbars and remove the ribbon."""
        if not self.ribbon_active:
            return

        # Remove ribbon
        if self.ribbon_toolbar:
            self.main_window.removeToolBar(self.ribbon_toolbar)
            self.ribbon_toolbar.deleteLater()
            self.ribbon_toolbar = None
            self.ribbon_widget = None

        # Restore menubar
        self.ribbon_active = False
        self.menubar_action.setChecked(False)
        menubar = self.main_window.menuBar()
        if self._original_menubar_max_height is not None:
            menubar.setMaximumHeight(self._original_menubar_max_height)
            self._original_menubar_max_height = None
        menubar.setVisible(True)

        # Check if all toolbars are false - if so, use defaults
        all_toolbars_false = all(
            not visible for visible in self._original_toolbar_visibility.values()
        )

        # Restore toolbars
        default_toolbars = {
            "mFileToolBar",
            "mDigitizeToolBar",
            "mMapNavToolBar",
            "mAttributesToolBar",
            "mPluginToolBar",
            "mSnappingToolBar",
            "mDataSourceManagerToolBar",
            "mSelectionToolBar",
        }
        for tb in self.main_window.findChildren(QToolBar):
            if tb.parent() != self.main_window or tb.isVisible() is True:
                continue
            name = tb.objectName()
            if name in self._original_toolbar_visibility:
                if all_toolbars_false:
                    # Show default toolbars if all were hidden
                    tb.setVisible(name in default_toolbars)
                else:
                    # Otherwise restore original visibility
                    tb.setVisible(self._original_toolbar_visibility[name])

        self.ribbon_active = False
        self.toggle_action.setChecked(False)
