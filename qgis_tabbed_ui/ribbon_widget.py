# -*- coding: utf-8 -*-
"""
Ribbon widget — a QTabWidget styled like a Microsoft Office ribbon.
Each tab corresponds to a QGIS menu. Within each tab, actions are
organized into labeled groups with large/small icon buttons. The
per-tab layout is configured in the tabs package (one module per tab).
"""

import re
from pathlib import Path

from qgis.PyQt import sip
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QAction,
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from .tabs import (
    ARRANGED_TABS,
    BUTTON_MENUS,
    DEFAULT_TAB,
    EXTRA_TAB_GROUPS,
    ICON_ONLY,
    ICON_OVERRIDES,
    LABELED_ACTIONS,
    MENU_GROUP_REPLACEMENTS,
    MERGED_TABS,
    SHORT_LABELS,
    TAB_ORDER,
    TOOLBAR_GROUP_OPTIONS,
    TOOLBAR_TABS,
    TRAILING_TAB_ORDER,
    plugins,
    styling,
)

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

# Submenus shown as popup buttons in "<Menu> Menu" groups:
# (menu objectName, submenu title)
MENU_POPUP_ACTIONS = {
    ("mRasterMenu", "Analysis"),
    ("mRasterMenu", "Projections"),
    ("mRasterMenu", "Miscellaneous"),
    ("mRasterMenu", "Extraction"),
    ("mRasterMenu", "Conversion"),
}

# Button sizes (px)
LARGE_ICON_SIZE = 28
LARGE_BUTTON_WIDTH = 56
LARGE_BUTTON_HEIGHT = 70
SMALL_ICON_SIZE = 18
SMALL_BUTTON_HEIGHT = 22
# Rows of small buttons per column in a group
DEFAULT_ROWS = 3

# Colors use palette() roles so the ribbon follows the active QGIS theme
# (e.g. Night Mapping) instead of hard-coded light colors.
RIBBON_STYLESHEET = """
QTabWidget::pane {
    border: 1px solid palette(mid);
    background: palette(window);
    margin: 0px;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar::tab {
    background: palette(button);
    border: 1px solid palette(mid);
    border-bottom: none;
    padding: 5px 14px;
    margin-right: 1px;
    font-weight: 500;
    min-width: 50px;
    color: palette(button-text);
}
QTabBar::tab:selected {
    background: palette(window);
    border-top: 2px solid palette(highlight);
    border-bottom: 1px solid palette(window);
    color: palette(window-text);
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    background: palette(midlight);
}
"""

GROUP_FRAME_STYLE = """
QFrame#ribbonGroup {
    border-right: 1px solid palette(mid);
    background: transparent;
    margin: 0px;
    padding: 0px 2px;
}
"""

GROUP_TITLE_STYLE = (
    "color: palette(window-text); font-size: 9px; padding: 0px; margin-top: 1px;"
)


class RibbonWidget(QTabWidget):
    """Microsoft Office-like ribbon interface for QGIS."""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        # action key -> entry name for actions without an objectName
        self._entry_names = {}
        self.main_window = iface.mainWindow()
        self.setStyleSheet(RIBBON_STYLESHEET)
        self.setMinimumHeight(95)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setUsesScrollButtons(True)
        self.setDocumentMode(False)

    def build_ribbon(self):
        """Populate the ribbon with tabs from QGIS menus and toolbars."""
        menubar = self.main_window.menuBar()
        all_toolbars = self._collect_all_toolbars()
        menus_by_name = self._collect_menus_by_name(menubar)

        # Build tabs in order
        for menu_name in TAB_ORDER:
            self._build_standard_menu_tab(menu_name, menus_by_name, all_toolbars)

        for title, toolbar_names in TOOLBAR_TABS:
            tab = self._build_toolbar_tab(toolbar_names, all_toolbars)
            if tab:
                self.addTab(tab, title)

        styling_tab = self._build_styling_tab(all_toolbars)
        if styling_tab:
            self.addTab(styling_tab, "Styling")

        for menu_name in TRAILING_TAB_ORDER:
            self._build_standard_menu_tab(menu_name, menus_by_name, all_toolbars)

    def _collect_all_toolbars(self):
        """Collect all toolbars from the main window."""
        all_toolbars = {}
        for tb in self.main_window.findChildren(QToolBar):
            name = tb.objectName()
            if name:
                all_toolbars[name] = tb
        return all_toolbars

    def _collect_menus_by_name(self, menubar):
        """Collect top-level menus by objectName."""
        menus_by_name = {}
        for menu in menubar.findChildren(QMenu):
            if menu.parent() == menubar:
                menus_by_name[menu.objectName()] = menu
        return menus_by_name

    def _get_mapped_toolbars_set(self):
        """Get the set of all toolbar names that are mapped to menus."""
        mapped_toolbars = set()
        for tb_list in MENU_TOOLBAR_MAP.values():
            mapped_toolbars.update(tb_list)
        mapped_toolbars.add("RibbonToolbarMain")

        # Additional known QGIS internal toolbars
        known_internal = {
            "mSnappingToolBar",
            "mLabelToolBar",
            "mAnnotationsToolBar",
            "mGpsToolBar",
            "mBookmarkToolbar",
            "mBrowserToolbar",
            "mSelectionToolBar",
            "mToolbar",
        }
        mapped_toolbars.update(known_internal)
        return mapped_toolbars

    def _make_tab_page(self):
        """Create a horizontally scrolling tab page. Returns (page, layout)."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)
        scroll.setWidget(container)
        return scroll, layout

    def _build_standard_menu_tab(self, menu_name, menus_by_name, all_toolbars):
        """Build a standard menu tab."""
        menu = menus_by_name.get(menu_name)
        if menu is None:
            return

        clean_title = menu.title().replace("&", "")
        if menu_name in ARRANGED_TABS:
            tabs = self._build_arranged_tabs(menu, menu_name, all_toolbars)
        else:
            menus = [
                (name, menus_by_name[name])
                for name in MERGED_TABS.get(menu_name, [])
                if name in menus_by_name
            ] + [(menu_name, menu)]
            tabs = [(None, self._build_tab(menus, all_toolbars))]
        for i, (title, tab) in enumerate(tabs):
            self.addTab(tab, title or clean_title)
            if menu_name == DEFAULT_TAB and i == 0:
                self.setCurrentWidget(tab)

    def _build_tab(self, menus, all_toolbars):
        """Build a single ribbon tab for one or more QGIS menus, given as
        (menu objectName, menu) pairs."""
        page, layout = self._make_tab_page()

        # Track action identities and toolbar-only actions
        seen_ids = set()
        empty_toolbar_action_ids = set()

        for menu_name, menu in menus:
            self._add_standard_groups(
                layout,
                menu,
                menu_name,
                all_toolbars,
                seen_ids,
                empty_toolbar_action_ids,
            )

        layout.addStretch()
        return page

    def _add_standard_groups(
        self,
        layout,
        menu,
        menu_name,
        all_toolbars,
        seen_ids,
        empty_toolbar_action_ids,
    ):
        """Add the groups of a standard (not arranged) menu tab to layout."""
        # Marked as seen so the menu group does not repeat them
        self._add_arranged_groups(layout, EXTRA_TAB_GROUPS.get(menu_name, []), seen_ids)

        # Add toolbar-based groups first
        self._add_toolbar_groups(
            layout,
            menu_name,
            all_toolbars,
            seen_ids,
            empty_toolbar_action_ids,
        )

        # If this is the Plugins menu tab, also add plugin toolbars
        if menu_name == "mPluginMenu":
            self._add_plugin_toolbars_to_tab(layout, seen_ids)

        # Add menu actions as a group
        self._add_menu_group(
            layout, menu, menu_name, seen_ids, empty_toolbar_action_ids
        )

    def _build_arranged_tabs(self, menu, menu_name, all_toolbars):
        """Build the tab(s) for a menu from its hand-arranged groups in
        ARRANGED_TABS. Returns a list of (title, tab widget)."""
        excluded, tab_specs = ARRANGED_TABS[menu_name]
        placed_ids = set()
        self._resolve_actions(excluded, placed_ids)

        # Resolve groups with "name/*" expansions last, so actions named
        # explicitly anywhere (even on a later tab) are not claimed by them
        def has_expansion(group):
            return any(
                isinstance(n, str) and n.endswith("/*")
                for n in group[1] + group[2]
            )

        all_groups = [g for _, groups in tab_specs for g in groups]
        resolved = {}
        for group in sorted(all_groups, key=has_expansion):
            resolved[id(group)] = (
                self._resolve_actions(group[1], placed_ids),
                self._resolve_actions(group[2], placed_ids),
            )

        tabs = []
        layouts = []
        for tab_title, groups in tab_specs:
            page, layout = self._make_tab_page()
            for group in groups:
                title, _, _, *options = group
                large_actions, small_actions = resolved[id(group)]
                if large_actions or small_actions:
                    layout.addWidget(
                        self._create_split_group(
                            title, large_actions, small_actions, *options
                        )
                    )
            tabs.append((tab_title, page))
            layouts.append(layout)

        # Keep anything not arranged above (e.g. added by plugins) reachable
        sources = list(menu.actions())
        for tb_name in MENU_TOOLBAR_MAP.get(menu_name, []):
            tb = all_toolbars.get(tb_name)
            if tb:
                sources += tb.actions()
        leftovers = []
        for action in sources:
            if action.isSeparator() or self._action_key(action) in placed_ids:
                continue
            placed_ids.add(self._action_key(action))
            leftovers.append(action)
        if leftovers:
            layouts[0].addWidget(self._create_split_group("More", [], leftovers))

        for layout in layouts:
            layout.addStretch()
        return tabs

    def _add_arranged_groups(self, layout, groups, placed_ids):
        """Add hand-arranged groups (see tabs/__init__.py) to layout, marking
        their actions as placed; empty groups are skipped. Returns whether
        any group was added."""
        added = False
        for title, large_names, small_names, *options in groups:
            large_actions = self._resolve_actions(large_names, placed_ids)
            small_actions = self._resolve_actions(small_names, placed_ids)
            if large_actions or small_actions:
                layout.addWidget(
                    self._create_split_group(
                        title, large_actions, small_actions, *options
                    )
                )
                added = True
        return added

    def _resolve_actions(self, names, placed_ids):
        """Look up actions by name (see tabs/__init__.py) and mark them,
        and the contents of their submenus, as placed."""
        actions = []

        def add(action):
            actions.append(action)
            placed_ids.add(self._action_key(action))
            if action.menu() is not None:
                placed_ids.update(
                    self._action_key(a) for a in action.menu().actions()
                )

        for name in names:
            if isinstance(name, tuple):
                label, entries = name
                entry_actions = self._resolve_actions(entries, placed_ids)
                if entry_actions:
                    # Parented to the ribbon so it lives as long as the button
                    menu = QMenu(label, self)
                    icons = [a.icon() for a in entry_actions if not a.icon().isNull()]
                    if icons:
                        menu.setIcon(icons[0])
                    menu.addActions(entry_actions)
                    add(menu.menuAction())
                continue
            if name.startswith("dock:"):
                dock = self.main_window.findChild(QDockWidget, name[len("dock:") :])
                if dock is not None:
                    action = dock.toggleViewAction()
                    # Toggle actions have no objectName; remember the entry
                    # name for SHORT_LABELS / ICON_ONLY / ICON_OVERRIDES
                    self._entry_names[self._action_key(action)] = name
                    add(action)
                continue
            expand = name.endswith("/*")
            name = name.removesuffix("/*")
            if ">" in name:
                parent_name, title = name.split(">", 1)
                menu = self._find_submenu(parent_name, title)
            else:
                menu = self.main_window.findChild(QMenu, name)
            if menu is not None:
                placed_ids.add(self._action_key(menu.menuAction()))
                if expand:
                    for a in menu.actions():
                        if not a.isSeparator() and (
                            self._action_key(a) not in placed_ids
                        ):
                            add(a)
                else:
                    add(menu.menuAction())
                continue
            action = self.main_window.findChild(QAction, name)
            if action is not None:
                add(action)
        return actions

    def _find_submenu(self, parent_name, title):
        """Find a submenu of a named menu by its (cleaned) title."""
        parent = self.main_window.findChild(QMenu, parent_name)
        if parent is None:
            return None
        for action in parent.actions():
            if action.menu() and self._clean_text(action.text()) == title:
                return action.menu()
        return None

    def _action_key(self, action):
        """Stable identity for an action (Python wrappers may be recreated)."""
        return sip.unwrapinstance(action)

    def _make_group_frame(self):
        """Create the framed container of a ribbon group. Returns (frame,
        its vertical layout)."""
        group = QFrame()
        group.setObjectName("ribbonGroup")
        group.setStyleSheet(GROUP_FRAME_STYLE)

        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(4, 2, 4, 0)
        main_layout.setSpacing(0)
        return group, main_layout

    def _create_split_group(self, title, large_actions, small_actions, options=None):
        """Create a group with large buttons followed by a column grid of
        small labelled buttons (see tabs/__init__.py for the options)."""
        options = options or {}
        rows = options.get("rows", DEFAULT_ROWS)
        icon_size = options.get("icon_size")
        group, main_layout = self._make_group_frame()

        row_layout = QHBoxLayout()
        row_layout.setSpacing(2)
        for action in large_actions:
            btn = self._make_arranged_button(action, True, group)
            if btn is not None:
                row_layout.addWidget(btn)
        small_buttons = [
            btn
            for btn in (
                self._make_arranged_button(
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
        self._add_group_title(main_layout, title)
        return group

    def _make_arranged_button(self, action, large, parent, labeled=True):
        """Create a labelled button for a split group; None if unsupported."""
        if isinstance(action, QWidgetAction):
            source = action.defaultWidget()
            if not isinstance(source, QToolButton):
                return None
            btn = self._clone_widget_button(
                source,
                large=large,
                parent=parent,
                popup=source.menu() is not None,
                labeled=labeled,
            )
        else:
            btn = self._make_button(
                action,
                large=large,
                popup=action.menu() is not None,
                labeled=labeled,
                parent=parent,
            )

        # Submenu actions usually have no objectName; use the menu's instead
        name = (
            self._entry_names.get(self._action_key(action))
            or action.objectName()
            or (action.menu().objectName() if action.menu() is not None else "")
        )
        short_label = SHORT_LABELS.get(name)
        icon_file = ICON_OVERRIDES.get(name)
        icon = None
        if icon_file:
            if not icon_file.startswith(":"):
                icon_file = str(Path(__file__).parent / "icons" / icon_file)
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

    def _create_toolbar_group(self, title, tb_name, actions):
        """Create the group for a toolbar's actions: a split group if the
        toolbar has TOOLBAR_GROUP_OPTIONS, otherwise a plain group."""
        if tb_name in TOOLBAR_GROUP_OPTIONS:
            return self._create_toolbar_split_group(
                title, actions, TOOLBAR_GROUP_OPTIONS[tb_name]
            )
        return self._create_group(title, actions)

    def _add_toolbar_groups(
        self, layout, menu_name, all_toolbars, seen_ids, empty_toolbar_action_ids
    ):
        """Add toolbar-based groups to the tab layout."""
        related_toolbars = MENU_TOOLBAR_MAP.get(menu_name, [])
        for tb_name in related_toolbars:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            title = tb.windowTitle() or tb_name
            layout.addWidget(self._create_toolbar_group(title, tb_name, tb.actions()))
            self._track_toolbar_actions(tb, seen_ids, empty_toolbar_action_ids)

    def _track_toolbar_actions(self, toolbar, seen_ids, empty_toolbar_action_ids):
        """Track which actions are from toolbars and which have no text."""
        for a in toolbar.actions():
            if a.isSeparator():
                continue
            action_id = self._action_key(a)
            seen_ids.add(action_id)
            if not self._clean_text(a.text()):
                empty_toolbar_action_ids.add(action_id)

    def _add_plugin_toolbars_to_tab(self, layout, seen_ids):
        """Add plugin toolbars to the Plugins menu tab."""
        mapped_toolbars = self._get_mapped_toolbars_set()
        for tb in self.main_window.findChildren(QToolBar):
            name = tb.objectName()
            if not name or name in mapped_toolbars or not tb.actions():
                continue
            group = self._create_toolbar_split_group(
                tb.windowTitle() or name, tb.actions(), plugins.PLUGIN_TOOLBAR_OPTIONS
            )
            layout.addWidget(group)
            for a in tb.actions():
                if a.isSeparator():
                    continue
                seen_ids.add(self._action_key(a))

    def _add_menu_group(
        self,
        layout,
        menu,
        menu_name,
        seen_ids,
        empty_toolbar_action_ids,
    ):
        """Add menu actions as a group, excluding actions already shown by toolbars."""
        if menu_name in MENU_GROUP_REPLACEMENTS:
            self._add_arranged_groups(
                layout, MENU_GROUP_REPLACEMENTS[menu_name], set()
            )
            return

        menu_actions = [
            a
            for a in menu.actions()
            if not a.isSeparator()
            and (
                self._action_key(a) not in seen_ids
                or self._action_key(a) in empty_toolbar_action_ids
            )
        ]
        if menu_actions:
            clean_title = menu.title().replace("&", "") + " Menu"
            layout.addWidget(
                self._create_group(clean_title, menu_actions, menu_name=menu_name)
            )

    def _build_styling_tab(self, all_toolbars):
        """Build the Styling tab (see tabs/styling.py); None if empty."""
        page, layout = self._make_tab_page()

        has_content = self._add_arranged_groups(
            layout, styling.LEADING_GROUPS, set()
        )

        for tb_name, title in styling.TOOLBARS:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            extra_actions = self._resolve_actions(
                styling.TOOLBAR_EXTRA_ENTRIES.get(tb_name, []), set()
            )
            layout.addWidget(
                self._create_toolbar_group(title, tb_name, tb.actions() + extra_actions)
            )
            has_content = True

        if self._add_arranged_groups(layout, styling.GROUPS, set()):
            has_content = True

        if not has_content:
            return None
        layout.addStretch()
        return page

    def _create_toolbar_split_group(self, title, actions, options):
        """Create a split group for toolbar actions (TOOLBAR_GROUP_OPTIONS)."""
        large_names = options.get("large", [])
        actions = [a for a in actions if not a.isSeparator()]
        if "only" in options:
            actions = [a for a in actions if a.objectName() in options["only"]]
        excluded = options.get("exclude", [])
        actions = [a for a in actions if a.objectName() not in excluded]
        return self._create_split_group(
            title,
            [a for a in actions if a.objectName() in large_names],
            [a for a in actions if a.objectName() not in large_names],
            options,
        )

    def _build_toolbar_tab(self, toolbar_names, all_toolbars):
        """Build a tab with one split group per toolbar (see TOOLBAR_TABS);
        None if none of the toolbars has actions."""
        page, layout = self._make_tab_page()

        has_content = False
        for tb_name in toolbar_names:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            layout.addWidget(
                self._create_toolbar_split_group(
                    tb.windowTitle() or tb_name,
                    tb.actions(),
                    TOOLBAR_GROUP_OPTIONS.get(tb_name, {}),
                )
            )
            has_content = True

        if not has_content:
            return None
        layout.addStretch()
        return page

    def _create_group(self, title, actions, menu_name=None):
        """Create a ribbon group: a framed grid of small buttons and a title.
        menu_name: the menu the actions come from (for MENU_POPUP_ACTIONS)."""
        group, main_layout = self._make_group_frame()
        main_layout.addLayout(self._create_small_button_grid(actions, menu_name, group))
        self._add_group_title(main_layout, title)
        return group

    def _add_group_title(self, main_layout, title):
        """Add the group title at the bottom of a group."""
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(GROUP_TITLE_STYLE)
        main_layout.addWidget(title_label)

    def _create_small_button_grid(self, actions, menu_name, parent):
        """Create a grid of small buttons, DEFAULT_ROWS per column; a
        separator starts a new column."""
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
            if isinstance(action, QWidgetAction):
                btn = self._clone_widget_button(action.defaultWidget(), parent=parent)
            else:
                btn = self._make_button(action, menu_name=menu_name, parent=parent)
            if btn is None:
                continue
            grid.addWidget(btn, row, col)
            row += 1
            if row >= DEFAULT_ROWS:
                row = 0
                col += 1
        return grid

    def _clean_text(self, text):
        return re.sub(r"<[^>]+>", "", (text or "").replace("&", "")).strip()

    def _action_popup_id(self, action):
        return action.objectName() or self._clean_text(action.text())

    def _style_button(self, btn, large, labeled, has_icon):
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

    def _clone_widget_button(
        self,
        source,
        large=False,
        parent=None,
        popup=False,
        labeled=False,
    ):
        """Clone a QToolButton from a QWidgetAction's defaultWidget.
        Returns None for non-QToolButton widgets (spinboxes, etc.).
        popup/labeled: as for _make_button."""
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
                self._clean_text(default_action.text() if default_action else "")
                or self._clean_text(source.toolTip())
            )
        self._style_button(clone, large, labeled, not source.icon().isNull())
        return clone

    def _sync_menu_button(self, button, action):
        """Keep a popup-only menu button aligned with its source action."""
        if sip.isdeleted(button):
            return
        button.setText(self._clean_text(action.text()))
        button.setIcon(action.icon())
        button.setToolTip(
            self._clean_text(action.toolTip()) or self._clean_text(action.text())
        )
        button.setStatusTip(action.statusTip())
        button.setEnabled(action.isEnabled())
        button.setVisible(action.isVisible())

    def _sync_popup_menu(self, popup_menu, source_menu):
        """Mirror the current actions from a source menu into a detached popup."""
        popup_menu.clear()
        popup_menu.addActions(source_menu.actions())

    def _make_button_menu(self, entries, parent):
        """Build a dropdown of relabelled proxies for BUTTON_MENUS entries."""
        menu = QMenu(parent)
        for name, label in entries:
            source = self.main_window.findChild(QAction, name)
            if source is None:
                continue
            proxy = menu.addAction(source.icon(), label)
            proxy.triggered.connect(source.trigger)

            def sync(proxy=proxy, source=source):
                if not sip.isdeleted(proxy):
                    proxy.setEnabled(source.isEnabled())

            sync()
            source.changed.connect(sync)
        return menu

    def _make_button(
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
            popup = (menu_name, self._action_popup_id(action)) in MENU_POPUP_ACTIONS
        if popup:
            source_menu = action.menu()
            self._sync_menu_button(btn, action)
            popup_menu = QMenu(btn)
            self._sync_popup_menu(popup_menu, source_menu)
            popup_menu.aboutToShow.connect(
                lambda popup_menu=popup_menu, action=action: self._sync_popup_menu(
                    popup_menu, action.menu()
                )
            )
            btn.setMenu(popup_menu)
            btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            action.changed.connect(
                lambda btn=btn, action=action: self._sync_menu_button(btn, action)
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
        self._style_button(btn, large, labeled, has_icon)
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
