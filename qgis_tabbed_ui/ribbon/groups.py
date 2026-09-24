# -*- coding: utf-8 -*-
"""Ribbon groups: framed sections of buttons with a title below."""

from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QPainter
from qgis.PyQt.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from ..tabs import TOOLBAR_GROUP_OPTIONS
from .styles import (
    DEFAULT_ROWS,
    GROUP_FRAME_STYLE,
    GROUP_TITLE_STYLE,
    divider_color,
)


class _GroupFrame(QFrame):
    """A ribbon group frame with a divider on its right edge (painted, so
    it follows theme changes)."""

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(divider_color(self.palette()))
        x = self.width() - 1
        painter.drawLine(x, 0, x, self.height() - 1)
        painter.end()


def _make_group_frame():
    """Create the framed container of a ribbon group. Returns (frame, its
    vertical layout)."""
    group = _GroupFrame()
    group.setObjectName("ribbonGroup")
    group.setStyleSheet(GROUP_FRAME_STYLE)

    main_layout = QVBoxLayout(group)
    main_layout.setContentsMargins(4, 2, 4, 0)
    main_layout.setSpacing(0)
    return group, main_layout


def _add_group_title(main_layout, title):
    """Add the group title at the bottom of a group."""
    title_label = QLabel(title)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet(GROUP_TITLE_STYLE)
    main_layout.addWidget(title_label)


class GroupFactory:
    """Creates ribbon groups, with buttons from a ButtonFactory."""

    def __init__(self, buttons):
        self.buttons = buttons

    def split_group(self, title, large_actions, small_actions, options=None):
        """Create a group with large buttons followed by a column grid of
        small labelled buttons (see tabs/__init__.py for the options)."""
        options = options or {}
        rows = options.get("rows", DEFAULT_ROWS)
        icon_size = options.get("icon_size")
        group, main_layout = _make_group_frame()

        row_layout = QHBoxLayout()
        row_layout.setSpacing(2)
        for action in large_actions:
            btn = self.buttons.make_arranged_button(action, True, group)
            if btn is not None:
                row_layout.addWidget(btn)
        small_buttons = [
            btn
            for btn in (
                self.buttons.make_arranged_button(
                    a, False, group, labeled=options.get("labels", True)
                )
                for a in small_actions
            )
            if btn is not None
        ]
        if small_buttons:
            grid = QGridLayout()
            grid.setSpacing(1)
            grid.setContentsMargins(0, 0, 0, 0)
            for i, btn in enumerate(small_buttons):
                if icon_size:
                    btn.setIconSize(QSize(icon_size, icon_size))
                    btn.setFixedHeight(icon_size + 8)
                    btn.setMinimumWidth(btn.sizeHint().width())
                grid.addWidget(
                    btn, i % rows, i // rows, alignment=Qt.AlignmentFlag.AlignLeft
                )
            row_layout.addLayout(grid)
            row_layout.setAlignment(grid, Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(row_layout)
        main_layout.addStretch()
        _add_group_title(main_layout, title)
        return group

    def toolbar_split_group(self, title, actions, options):
        """Create a split group for toolbar actions (TOOLBAR_GROUP_OPTIONS)."""
        large_names = options.get("large", [])
        actions = [a for a in actions if not a.isSeparator()]
        if "only" in options:
            actions = [a for a in actions if a.objectName() in options["only"]]
        excluded = options.get("exclude", [])
        actions = [a for a in actions if a.objectName() not in excluded]
        return self.split_group(
            title,
            [a for a in actions if a.objectName() in large_names],
            [a for a in actions if a.objectName() not in large_names],
            options,
        )

    def toolbar_group(self, title, tb_name, actions):
        """Create the group for a toolbar's actions: a split group if the
        toolbar has TOOLBAR_GROUP_OPTIONS, otherwise a plain group."""
        if tb_name in TOOLBAR_GROUP_OPTIONS:
            return self.toolbar_split_group(
                title, actions, TOOLBAR_GROUP_OPTIONS[tb_name]
            )
        return self.plain_group(title, actions)

    def plain_group(self, title, actions, menu_name=None):
        """Create a group of small buttons, DEFAULT_ROWS per column; a
        separator starts a new column. menu_name: the menu the actions come
        from (for MENU_POPUP_ACTIONS)."""
        group, main_layout = _make_group_frame()
        grid = QGridLayout()
        grid.setSpacing(1)
        grid.setContentsMargins(0, 0, 0, 0)
        row, col = 0, 0
        for action in actions:
            if action.isSeparator():
                if row > 0:
                    col += 1
                    row = 0
                continue
            btn = self.buttons.make_small_button(action, menu_name, group)
            if btn is None:
                continue
            grid.addWidget(btn, row, col)
            row += 1
            if row >= DEFAULT_ROWS:
                row = 0
                col += 1
        main_layout.addLayout(grid)
        _add_group_title(main_layout, title)
        return group
