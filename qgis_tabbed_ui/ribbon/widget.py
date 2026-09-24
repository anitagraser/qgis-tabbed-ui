# -*- coding: utf-8 -*-
"""The ribbon widget: builds one tab per TAB of the tabs package."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QToolBar,
    QWidget,
)

from ..tabs import TABS, TOOLBAR_GROUP_OPTIONS
from ..tabs.spec import ArrangedTab, MenuTab
from .actions import ActionResolver, action_key, clean_text
from .buttons import ButtonFactory
from .groups import GroupFactory
from .qgis_ui import MENU_TOOLBAR_MAP, collect_menus, collect_toolbars, is_plugin_toolbar
from .styles import RIBBON_STYLESHEET


def _make_tab_page():
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


def _menu_title(menu):
    return menu.title().replace("&", "")


class RibbonWidget(QTabWidget):
    """Microsoft Office-like ribbon interface for QGIS."""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.main_window = iface.mainWindow()
        self._resolver = ActionResolver(self.main_window, menu_parent=self)
        self._groups = GroupFactory(ButtonFactory(self.main_window, self._resolver))
        self.setStyleSheet(RIBBON_STYLESHEET)
        self.setMinimumHeight(95)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setUsesScrollButtons(True)
        self.setDocumentMode(False)

    def build_ribbon(self):
        """Populate the ribbon with the tabs in TABS (see tabs/spec.py)."""
        all_toolbars = collect_toolbars(self.main_window)
        menus_by_name = collect_menus(self.main_window.menuBar())
        arranged_tabs = self._build_arranged_tabs(menus_by_name, all_toolbars)

        for spec in TABS:
            if isinstance(spec, ArrangedTab):
                tab = arranged_tabs.get(spec)
            elif isinstance(spec, MenuTab):
                tab = self._build_menu_tab(spec, menus_by_name, all_toolbars)
            else:
                tab = self._build_toolbar_tab(spec, all_toolbars)
            if tab is None:
                continue
            title, page = tab
            self.addTab(page, title)
            if spec.default:
                self.setCurrentWidget(page)

    def _add_arranged_groups(self, layout, groups, placed_ids):
        """Add hand-arranged groups (see tabs/__init__.py) to layout, marking
        their actions as placed; empty groups are skipped. Returns whether
        any group was added."""
        added = False
        for title, large_names, small_names, *options in groups:
            large_actions = self._resolver.resolve(large_names, placed_ids)
            small_actions = self._resolver.resolve(small_names, placed_ids)
            if large_actions or small_actions:
                layout.addWidget(
                    self._groups.split_group(
                        title, large_actions, small_actions, *options
                    )
                )
                added = True
        return added

    # ArrangedTab

    def _build_arranged_tabs(self, menus_by_name, all_toolbars):
        """Build all ArrangedTabs, resolving the tabs of each menu together.
        Returns {spec: (title, page)}; tabs whose menu is missing are left
        out."""
        specs_by_menu = {}
        for spec in TABS:
            if isinstance(spec, ArrangedTab):
                specs_by_menu.setdefault(spec.menu, []).append(spec)

        built = {}
        for menu_name, specs in specs_by_menu.items():
            menu = menus_by_name.get(menu_name)
            if menu is None:
                continue
            placed_ids = set()
            for spec in specs:
                self._resolver.resolve(spec.excluded, placed_ids)

            # Resolve groups with "name/*" expansions last, so actions named
            # explicitly anywhere (even on a later tab) are not claimed by them
            def has_expansion(group):
                return any(
                    isinstance(n, str) and n.endswith("/*")
                    for n in group[1] + group[2]
                )

            all_groups = [g for spec in specs for g in spec.groups]
            resolved = {}
            for group in sorted(all_groups, key=has_expansion):
                resolved[id(group)] = (
                    self._resolver.resolve(group[1], placed_ids),
                    self._resolver.resolve(group[2], placed_ids),
                )

            layouts = []
            for spec in specs:
                page, layout = _make_tab_page()
                for group in spec.groups:
                    title, _, _, *options = group
                    large_actions, small_actions = resolved[id(group)]
                    if large_actions or small_actions:
                        layout.addWidget(
                            self._groups.split_group(
                                title, large_actions, small_actions, *options
                            )
                        )
                built[spec] = (spec.title or _menu_title(menu), page)
                layouts.append(layout)

            # Keep anything not arranged above (e.g. added by plugins) reachable
            sources = list(menu.actions())
            for tb_name in MENU_TOOLBAR_MAP.get(menu_name, []):
                tb = all_toolbars.get(tb_name)
                if tb:
                    sources += tb.actions()
            leftovers = []
            for action in sources:
                if action.isSeparator() or action_key(action) in placed_ids:
                    continue
                placed_ids.add(action_key(action))
                leftovers.append(action)
            if leftovers:
                layouts[0].addWidget(self._groups.split_group("More", [], leftovers))

            for layout in layouts:
                layout.addStretch()
        return built

    # MenuTab

    def _build_menu_tab(self, spec, menus_by_name, all_toolbars):
        """Build a MenuTab. Returns (title, page), None if its menu is
        missing."""
        menu = menus_by_name.get(spec.menu)
        if menu is None:
            return None
        page, layout = _make_tab_page()

        # Track action identities and toolbar-only actions
        seen_ids = set()
        empty_toolbar_action_ids = set()

        # Marked as seen so the menu groups do not repeat them
        self._add_arranged_groups(layout, spec.leading_groups, seen_ids)

        menus = [
            (name, menus_by_name[name])
            for name in spec.merged_menus
            if name in menus_by_name
        ] + [(spec.menu, menu)]
        for menu_name, m in menus:
            self._add_toolbar_groups(
                layout, menu_name, all_toolbars, seen_ids, empty_toolbar_action_ids
            )
            if menu_name == spec.menu and spec.plugin_toolbar_options is not None:
                self._add_plugin_toolbars(
                    layout, spec.plugin_toolbar_options, seen_ids
                )
            self._add_menu_group(
                layout,
                m,
                menu_name,
                spec.menu_groups,
                seen_ids,
                empty_toolbar_action_ids,
            )

        layout.addStretch()
        return spec.title or _menu_title(menu), page

    def _add_toolbar_groups(
        self, layout, menu_name, all_toolbars, seen_ids, empty_toolbar_action_ids
    ):
        """Add a group per toolbar related to the menu (MENU_TOOLBAR_MAP)."""
        for tb_name in MENU_TOOLBAR_MAP.get(menu_name, []):
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            title = tb.windowTitle() or tb_name
            layout.addWidget(self._groups.toolbar_group(title, tb_name, tb.actions()))
            # Track which actions are from toolbars and which have no text
            for a in tb.actions():
                if a.isSeparator():
                    continue
                seen_ids.add(action_key(a))
                if not clean_text(a.text()):
                    empty_toolbar_action_ids.add(action_key(a))

    def _add_plugin_toolbars(self, layout, options, seen_ids):
        """Add a split group with the given options per third-party plugin
        toolbar."""
        for tb in self.main_window.findChildren(QToolBar):
            name = tb.objectName()
            if not name or not is_plugin_toolbar(name) or not tb.actions():
                continue
            layout.addWidget(
                self._groups.toolbar_split_group(
                    tb.windowTitle() or name, tb.actions(), options
                )
            )
            for a in tb.actions():
                if not a.isSeparator():
                    seen_ids.add(action_key(a))

    def _add_menu_group(
        self,
        layout,
        menu,
        menu_name,
        replacements,
        seen_ids,
        empty_toolbar_action_ids,
    ):
        """Add menu actions as a group, excluding actions already shown by
        toolbars, or the menu's replacement groups (MenuTab.menu_groups)."""
        if menu_name in replacements:
            self._add_arranged_groups(layout, replacements[menu_name], set())
            return

        menu_actions = [
            a
            for a in menu.actions()
            if not a.isSeparator()
            and (
                action_key(a) not in seen_ids
                or action_key(a) in empty_toolbar_action_ids
            )
        ]
        if menu_actions:
            layout.addWidget(
                self._groups.plain_group(
                    _menu_title(menu) + " Menu", menu_actions, menu_name=menu_name
                )
            )

    # ToolbarTab

    def _build_toolbar_tab(self, spec, all_toolbars):
        """Build a ToolbarTab. Returns (title, page), None if empty."""
        page, layout = _make_tab_page()

        has_content = self._add_arranged_groups(layout, spec.leading_groups, set())

        for tb_name, title in spec.toolbars:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            extra_actions = self._resolver.resolve(
                spec.toolbar_extra_entries.get(tb_name, []), set()
            )
            layout.addWidget(
                self._groups.toolbar_split_group(
                    title or tb.windowTitle() or tb_name,
                    tb.actions() + extra_actions,
                    TOOLBAR_GROUP_OPTIONS.get(tb_name, {}),
                )
            )
            has_content = True

        if self._add_arranged_groups(layout, spec.trailing_groups, set()):
            has_content = True

        if not has_content:
            return None
        layout.addStretch()
        return spec.title, page
