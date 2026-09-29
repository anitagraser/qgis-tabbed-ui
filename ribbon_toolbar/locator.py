# -*- coding: utf-8 -*-
"""Moves the QGIS locator search box from the status bar into the ribbon's
tab row, and back."""

import re

from qgis.gui import QgsFloatingWidget
from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QLineEdit, QWidget


class RibbonLocator:
    """The QGIS locator widget while it is moved into the ribbon, and what is
    needed to put it back into the status bar."""

    # Width of the locator search box in the ribbon's tab row (px)
    WIDTH = 300
    # Placeholder of the locator search box while the ribbon is active; the
    # shortcut of QGIS' own placeholder ("Type to locate (Ctrl+K)") is kept
    PLACEHOLDER = "Search tools, layers, places…"

    def __init__(self, iface):
        self.iface = iface
        self.main_window = iface.mainWindow()
        self._locator = None
        self._state = None

    def _results_popup(self, locator):
        """The floating results list of the locator widget, if found."""
        # QGIS returns it as a plain QWidget, like the locator widget
        for widget in self.main_window.findChildren(QWidget):
            if widget.metaObject().className() != "QgsFloatingWidget":
                continue
            popup = sip.cast(widget, QgsFloatingWidget)
            anchor = popup.anchorWidget()
            if anchor is not None and (
                anchor is locator or locator.isAncestorOf(anchor)
            ):
                return popup
        return None

    def move_into(self, layout):
        """Move the QGIS locator widget from the status bar into layout,
        its results list opening below it instead of above."""
        # Found by name: QGIS returns it as a plain QWidget, not a
        # QgsLocatorWidget
        locator = self.main_window.findChild(QWidget, "LocatorWidget")
        if locator is None:
            return
        parent = locator.parentWidget()
        parent_layout = parent.layout() if parent is not None else None
        index = parent_layout.indexOf(locator) if parent_layout else -1
        line_edit = locator.findChild(QLineEdit)
        popup = self._results_popup(locator)
        self._state = {
            "layout": parent_layout,
            "index": index,
            "stretch": parent_layout.stretch(index) if index >= 0 else 0,
            "alignment": (
                parent_layout.itemAt(index).alignment() if index >= 0 else None
            ),
            "min_width": locator.minimumWidth(),
            "max_width": locator.maximumWidth(),
            "placeholder": line_edit.placeholderText() if line_edit else None,
            "popup": popup,
            "popup_points": (
                (popup.anchorPoint(), popup.anchorWidgetPoint()) if popup else None
            ),
        }
        self._locator = locator

        layout.addWidget(locator)
        locator.setFixedWidth(self.WIDTH)
        if line_edit is not None:
            shortcut = re.search(r"\([^()]+\)$", line_edit.placeholderText())
            line_edit.setPlaceholderText(
                self.PLACEHOLDER + (" " + shortcut.group(0) if shortcut else "")
            )
        if popup is not None:
            # Right-aligned: the list is wider than the box (half the window)
            popup.setAnchorPoint(QgsFloatingWidget.AnchorPoint.TopRight)
            popup.setAnchorWidgetPoint(QgsFloatingWidget.AnchorPoint.BottomRight)

    def restore(self):
        """Put the locator widget back where it was in the status bar.
        Must run before the ribbon is deleted, which would delete it too."""
        locator, state = self._locator, self._state
        self._locator = None
        self._state = None
        if locator is None or sip.isdeleted(locator):
            return
        locator.setMinimumWidth(state["min_width"])
        locator.setMaximumWidth(state["max_width"])
        line_edit = locator.findChild(QLineEdit)
        if line_edit is not None and state["placeholder"] is not None:
            line_edit.setPlaceholderText(state["placeholder"])
        popup = state["popup"]
        if popup is not None and not sip.isdeleted(popup):
            anchor_point, anchor_widget_point = state["popup_points"]
            popup.setAnchorPoint(anchor_point)
            popup.setAnchorWidgetPoint(anchor_widget_point)
        layout = state["layout"]
        if layout is None or sip.isdeleted(layout):
            # Keep it alive (and reachable) rather than lose it with the ribbon
            self.iface.statusBarIface().addPermanentWidget(
                locator, 0, self.iface.statusBarIface().AnchorLeft
            )
            return
        index = min(max(state["index"], 0), layout.count())
        if state["alignment"] is not None:
            layout.insertWidget(index, locator, state["stretch"], state["alignment"])
        else:
            layout.insertWidget(index, locator, state["stretch"])
        locator.show()
