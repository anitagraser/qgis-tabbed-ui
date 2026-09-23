# -*- coding: utf-8 -*-
"""
Ribbon widget — a QTabWidget styled like a Microsoft Office ribbon.
Each tab corresponds to a QGIS menu. Within each tab, actions are
organized into labeled groups with large/small icon buttons.
"""

import re
from pathlib import Path

from qgis.PyQt import sip
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QAction,
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

# Tab ordering — controls the order tabs appear in the ribbon
TAB_ORDER = [
    "mProjectMenu",
    "mViewMenu",
    "mEditMenu",
    "mRasterMenu",
    "mVectorMenu",
    "mMeshMenu",
    "mDatabaseMenu",
    "mWebMenu",
    "mPluginMenu",
]

# Hand-arranged groups for tabs listed in ARRANGED_TABS, LibreOffice style:
# (title, large buttons, small buttons). Entries are QAction or QMenu
# objectNames, or "menuName>Submenu Title" for submenus without an
# objectName; a menu entry becomes a popup button, "name/*" expands a
# menu into its individual actions (those not placed yet), and a
# ("Label", [entries]) tuple becomes a popup button with those entries.
# Missing names are skipped, and actions
# from the tab's menu / toolbars not listed here end up in a "More" group.
# An optional 4th element holds layout options for the small buttons:
# {"rows": number of rows (default 3), "icon_size": icon size in px,
#  "labels": False to show small buttons compactly (icon only if they
#  have an icon, otherwise text only)}.
PROJECT_TAB_GROUPS = [
    ("New", ["mActionNewProject"], ["mProjectFromTemplateMenu"]),
    (
        "Open",
        ["mActionOpenProject"],
        ["mRecentProjectsMenu", "mProjectFromStorageMenu", "mActionCloseProject"],
    ),
    (
        "Save",
        ["mActionSaveProject"],
        ["mActionSaveProjectAs", "mProjectToStorageMenu", "mActionRevertProject"],
    ),
    (
        "Project Settings",
        ["mActionProjectProperties"],
        ["mActionSnappingOptions", "mActionStyleManager", "mProjectMenu>Models"],
    ),
    (
        "Layouts",
        ["mActionNewPrintLayout"],
        ["mActionNewReport", "mActionShowLayoutManager", "mLayoutsMenu"],
    ),
    (
        "Import/Export",
        [],
        [
            ("Export Map to…", ["mActionSaveMapAsImage", "mActionSaveMapAsPdf"]),
            ("DWG/DXF", ["mActionDxfExport", "mActionDwgImport"]),
            "menuImport_Export/*",
        ],
    ),
]

HOME_TAB_GROUPS = [
    ("Layer", ["mActionDataSourceManager"], ["mLayerMenu/*"], {"labels": False}),
    (
        "Identify",
        ["mActionIdentify"],
        ["mActionMapTips", "ActionFeatureAction", "mViewMenu>Measure"],
    ),
    (
        "Pan",
        ["mActionPan"],
        ["mActionPanToSelected", "mActionNewBookmark", "mActionShowBookmarkManager"],
    ),
    (
        "Zoom",
        ["mActionZoomIn", "mActionZoomOut"],
        [
            "mActionZoomFullExtent",
            "mActionZoomToSelected",
            "mActionZoomToLayers",
            "mActionZoomLast",
            "mActionZoomNext",
            "mActionZoomActualSize",
        ],
        {"rows": 2, "icon_size": 24},
    ),
    (
        "Selection",
        ["mActionSelectFeatures"],
        [
            "mActionSelectPolygon",
            "mActionSelectFreehand",
            "mActionSelectRadius",
            "mActionSelectByForm",
            "mActionSelectByExpression",
            "mActionSelectAll",
            "mActionInvertSelection",
            "mActionReselect",
            "mActionDeselectAll",
            "mActionDeselectActiveLayer",
        ],
        {"rows": 2, "icon_size": 24},
    ),
    (
        "Attributes",
        ["ActionOpenTable"],
        ["mActionOpenFieldCalc", "mActionStatisticalSummary", "mMenuFilterTable"],
    ),
]

VIEW_TAB_GROUPS = [
    ("Map Views", ["mActionNewMapCanvas"], ["mViewMenu>3D Map Views", "mActionDraw"]),
    (
        "Display",
        [],
        [
            "mViewMenu>Data Filtering",
            "mViewMenu>Elevation Profiles",
            "mViewMenu>Decorations",
            "mViewMenu>Preview Mode",
            "mViewMenu>Layer Visibility",
        ],
    ),
    (
        "Overview",
        [],
        [
            "mActionAddToOverview",
            "mActionAddAllToOverview",
            "mActionRemoveAllFromOverview",
        ],
    ),
    ("Processing", ["toolboxAction"], []),
]

# Actions left out of the Home and View tabs (ActionMeasure duplicates
# the Measure submenu)
VIEW_MENU_EXCLUDED = [
    "mViewMenu>Panels",
    "mViewMenu>Toolbars",
    "mActionToggleFullScreen",
    "mActionTogglePanelsVisibility",
    "mActionToggleMapOnly",
    "mActionShowBookmarks",
    "ActionMeasure",
    # Layer menu actions left out of the Home tab's Layer group
    # (mActionOpenTable duplicates the Attribute Table button)
    "mActionOpenTable",
    "mActionLayerSaveAs",
    "mActionSaveLayerDefinition",
    "mActionLayerProperties",
    "mActionSetLayerScaleVisibility",
    "mActionSetLayerCRS",
    "mActionSetProjectCRSFromLayer",
    "mActionLabeling",
    "mActionRemoveLayer",
    "mActionLayerSubsetString",
    "mActionDuplicateLayer",
    "mActionCopyLayer",
    "mActionPasteLayer",
    # Shown on the Raster / Edit tab instead
    "mActionShowGeoreferencer",
    "mActionToggleEditing",
    "mActionSaveLayerEdits",
    "mActionAllEdits",
    "mAddLayerMenu",
]

# Shorter button labels for arranged tabs (tooltips keep the full text)
SHORT_LABELS = {
    "mProjectFromTemplateMenu": "From Template",
    "mActionDataSourceManager": "Add Layer",
    "mActionIdentify": "Identify",
    "mActionPan": "Pan",
    "mActionPanToSelected": "Pan to Selection",
    "mActionNewBookmark": "New Bookmark",
    "mActionShowBookmarkManager": "Bookmark Manager",
    "ActionOpenTable": "Attribute Table",
    "mActionOpenFieldCalc": "Field Calculator",
    "mActionStatisticalSummary": "Statistics",
}

# Plugin-provided icons for arranged-tab buttons whose action has none
ICON_OVERRIDES = {
    "mActionReselect": "reselect.svg",
}

# Buttons on arranged tabs shown without a label (tooltips keep the text)
ICON_ONLY = {
    "mActionZoomIn",
    "mActionZoomOut",
    "mActionZoomFullExtent",
    "mActionZoomToSelected",
    "mActionZoomToLayers",
    "mActionZoomLast",
    "mActionZoomNext",
    "mActionZoomActualSize",
    "mActionSelectPolygon",
    "mActionSelectFreehand",
    "mActionSelectRadius",
    "mActionSelectByForm",
    "mActionSelectByExpression",
    "mActionSelectAll",
    "mActionInvertSelection",
    "mActionReselect",
    "mActionDeselectAll",
    "mActionDeselectActiveLayer",
}

# menu objectName -> (excluded entries, [(tab title, groups), ...]).
# A menu can be split over several tabs; a tab title of None uses the menu
# title, and unarranged actions go into a "More" group on the first tab.
ARRANGED_TABS = {
    "mProjectMenu": (["mActionExit"], [(None, PROJECT_TAB_GROUPS)]),
    "mViewMenu": (
        VIEW_MENU_EXCLUDED,
        [("Home", HOME_TAB_GROUPS), ("View", VIEW_TAB_GROUPS)],
    ),
}

# Extra hand-arranged groups (see PROJECT_TAB_GROUPS) placed at the start
# of standard (not arranged) tabs, e.g. for actions from other menus
EXTRA_TAB_GROUPS = {
    "mRasterMenu": [("Georeferencer", ["mActionShowGeoreferencer"], [])],
}

# Tab shown when the ribbon is created
DEFAULT_TAB = "mViewMenu"

# Toolbar groups that count as "primary" (get large icons)
LARGE_ICONS = {
    "mFileToolBar",
    "mMapNavToolBar",
    "mDigitizeToolBar",
    "mDataSourceManagerToolBar",
    "mSelectionToolBar",
    "mSettingsMenu",
    "processingToolbar",
    "processing",
    "mPluginMenu",
    "mPluginToolBar",
}

MENU_POPUP_ACTIONS = {
    ("mProjectMenu", "New from Template"),
    ("mProjectMenu", "Open From"),
    ("mProjectMenu", "Open Recent"),
    ("mProjectMenu", "Save To"),
    ("mProjectMenu", "Import/Export"),
    ("mProjectMenu", "Layouts"),
    ("mProjectMenu", "Models"),
    ("mEditMenu", "Paste Features As"),
    ("mEditMenu", "Add Annotation"),
    ("mEditMenu", "Edit Attributes"),
    ("mEditMenu", "Edit Geometry"),
    ("mViewMenu", "3D Map Views"),
    ("mViewMenu", "Data Filtering"),
    ("mViewMenu", "Measure"),
    ("mViewMenu", "Decorations"),
    ("mViewMenu", "Preview Mode"),
    ("mViewMenu", "Layer Visibility"),
    ("mViewMenu", "Panels"),
    ("mViewMenu", "Toolbars"),
    ("mLayerMenu", "Create Layer"),
    ("mLayerMenu", "Add Layer"),
    ("mLayerMenu", "Filter Attribute Table"),
    ("mLayerMenu", "mActionAllEdits"),
    ("mSettingsMenu", "User Profiles"),
    ("mPluginMenu", "Plugin Reloader"),
    ("mPluginMenu", "QGIS MCP"),
    ("mPluginMenu", "qt6_compat"),
    ("mPluginMenu", "Ribbon Toolbar"),
    ("mRasterMenu", "Analysis"),
    ("mRasterMenu", "Projections"),
    ("mRasterMenu", "Miscellaneous"),
    ("mRasterMenu", "Extraction"),
    ("mRasterMenu", "Conversion"),
    ("mVectorMenu", "Analysis Tools"),
    ("mVectorMenu", "Geoprocessing Tools"),
    ("mVectorMenu", "Geometry Tools"),
    ("mVectorMenu", "Research Tools"),
    ("mVectorMenu", "Data Management Tools"),
    ("mHelpMenu", "Plugins"),
}

TOOLBAR_POPUP_ACTIONS = {
    ("mDigitizeToolBar", "mActionAllEdits"),
    ("mSnappingToolBar", "EnableTracingAction"),
}

WIDGET_POPUP_BUTTONS = {
    ("mAnnotationsToolBar", "mActionCreateAnnotationLayer"),
    ("mAttributesToolBar", "mActionFeatureAction"),
    ("mDigitizeToolBar", "mActionDigitizeWithSegment"),
    ("mGpsToolBar", "Set destination layer for GPS digitized features"),
    ("mGpsToolBar", "Settings"),
    ("mMeshToolBar", "Digitize Mesh Elements"),
    ("mMeshToolBar", "Force by Selected Geometries"),
    ("mPluginToolBar", "PluginReloader_ReloadRecentPlugin"),
    ("mShapeDigitizeToolBar", "Circle from 2 points"),
    ("mShapeDigitizeToolBar", "Ellipse from center and 2 points"),
    ("mShapeDigitizeToolBar", "Rectangle from center and a point"),
    ("mShapeDigitizeToolBar", "Regular polygon from 2 points"),
    ("mSnappingToolBar", "All Layers"),
    ("mSnappingToolBar", "Allow Overlap"),
    ("mSnappingToolBar", "Edit advanced configuration"),
    ("mSnappingToolBar", "Vertex"),
    ("processingToolbar", "Models"),
    ("processingToolbar", "Scripts"),
}

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

        # "Extra" tab for additional toolbars (Snapping, Labels, Selection, etc.)
        extra_tab = self._build_extra_tab(all_toolbars)
        if extra_tab:
            self.addTab(extra_tab, "Tools")

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

    def _collect_plugin_toolbars(self, all_toolbars):
        """Collect toolbars not mapped to any menu."""
        mapped_toolbars = self._get_mapped_toolbars_set()
        plugin_toolbars = []
        for name, tb in all_toolbars.items():
            if name not in mapped_toolbars and tb.actions():
                plugin_toolbars.append(tb)
        return plugin_toolbars

    def _build_standard_menu_tab(self, menu_name, menus_by_name, all_toolbars):
        """Build a standard menu tab."""
        menu = menus_by_name.get(menu_name)
        if menu is None:
            return

        clean_title = menu.title().replace("&", "")
        if menu_name in ARRANGED_TABS:
            tabs = self._build_arranged_tabs(menu, menu_name, all_toolbars)
        else:
            tabs = [(None, self._build_tab(menu, all_toolbars, menu_name))]
        for i, (title, tab) in enumerate(tabs):
            self.addTab(tab, title or clean_title)
            if menu_name == DEFAULT_TAB and i == 0:
                self.setCurrentWidget(tab)

    def _build_tab(self, menu, all_toolbars, menu_name):
        """Build a single ribbon tab for a QGIS menu."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        # Track action identities and toolbar-only actions
        seen_ids = set()
        empty_toolbar_action_ids = set()

        for title, large_names, small_names, *options in EXTRA_TAB_GROUPS.get(
            menu_name, []
        ):
            large_actions = self._resolve_actions(large_names, set())
            small_actions = self._resolve_actions(small_names, set())
            if large_actions or small_actions:
                layout.addWidget(
                    self._create_split_group(
                        title, large_actions, small_actions, *options
                    )
                )

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

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

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

            for group in groups:
                title, _, _, *options = group
                large_actions, small_actions = resolved[id(group)]
                if large_actions or small_actions:
                    layout.addWidget(
                        self._create_split_group(
                            title, large_actions, small_actions, *options
                        )
                    )
            tabs.append((tab_title, scroll))
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

    def _resolve_actions(self, names, placed_ids):
        """Look up actions by name (see PROJECT_TAB_GROUPS) and mark them,
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

    def _create_split_group(self, title, large_actions, small_actions, options=None):
        """Create a group with large buttons followed by a column grid of
        small labelled buttons (see PROJECT_TAB_GROUPS for the options)."""
        options = options or {}
        rows = options.get("rows", 3)
        icon_size = options.get("icon_size")
        group = QFrame()
        group.setObjectName("ribbonGroup")
        group.setStyleSheet(GROUP_FRAME_STYLE)

        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(4, 2, 4, 0)
        main_layout.setSpacing(0)

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
        name = action.objectName() or (
            action.menu().objectName() if action.menu() is not None else ""
        )
        short_label = SHORT_LABELS.get(name)
        icon_file = ICON_OVERRIDES.get(name)
        icon = QIcon(str(Path(__file__).parent / icon_file)) if icon_file else None
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

    def _add_toolbar_groups(
        self, layout, menu_name, all_toolbars, seen_ids, empty_toolbar_action_ids
    ):
        """Add toolbar-based groups to the tab layout."""
        related_toolbars = MENU_TOOLBAR_MAP.get(menu_name, [])
        for tb_name in related_toolbars:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            is_primary = tb_name in LARGE_ICONS
            title = tb.windowTitle() or tb_name
            group = self._create_group(
                title,
                tb.actions(),
                large=is_primary,
                source_kind="toolbar",
                source_name=tb_name,
            )
            layout.addWidget(group)
            self._track_toolbar_actions(tb, seen_ids, empty_toolbar_action_ids)

    def _track_toolbar_actions(self, toolbar, seen_ids, empty_toolbar_action_ids):
        """Track which actions are from toolbars and which have no text."""
        for a in toolbar.actions():
            if a.isSeparator():
                continue
            action_id = id(a)
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
            group = self._create_group(
                tb.windowTitle() or name,
                tb.actions(),
                large=False,
                source_kind="toolbar",
                source_name=name,
            )
            layout.addWidget(group)
            for a in tb.actions():
                if a.isSeparator():
                    continue
                seen_ids.add(id(a))

    def _add_menu_group(
        self,
        layout,
        menu,
        menu_name,
        seen_ids,
        empty_toolbar_action_ids,
    ):
        """Add menu actions as a group, excluding actions already shown by toolbars."""
        menu_actions = [
            a
            for a in menu.actions()
            if not a.isSeparator()
            and (id(a) not in seen_ids or id(a) in empty_toolbar_action_ids)
        ]
        if menu_actions:
            clean_title = menu.title().replace("&", "") + " Menu"
            group = self._create_group(
                clean_title,
                menu_actions,
                large=menu_name in LARGE_ICONS,
                source_kind="menu",
                source_name=menu_name,
            )
            layout.addWidget(group)

    def _build_extra_tab(self, all_toolbars):
        """Build the 'Tools' tab for additional QGIS toolbars."""
        extra_names = [
            ("mSnappingToolBar", "Snapping"),
            ("mLabelToolBar", "Labels"),
            ("mSelectionToolBar", "Selection"),
            ("mAnnotationsToolBar", "Annotations"),
            ("mGpsToolBar", "GPS"),
        ]
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        has_content = False
        for tb_name, title in extra_names:
            tb = all_toolbars.get(tb_name)
            if not tb or not tb.actions():
                continue
            is_primary = tb_name in LARGE_ICONS
            group = self._create_group(
                title,
                tb.actions(),
                large=is_primary,
                source_kind="toolbar",
                source_name=tb_name,
            )
            layout.addWidget(group)
            has_content = True

        layout.addStretch()
        if has_content:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setWidget(container)
            return scroll
        return None

    def _build_plugins_extra_tab(self, plugin_toolbars):
        """Build additional groups for plugin toolbars."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)
        for tb in plugin_toolbars:
            title = tb.windowTitle() or tb.objectName()
            group = self._create_group(
                title,
                tb.actions(),
                large=False,
                source_kind="toolbar",
                source_name=tb.objectName(),
            )
            layout.addWidget(group)
        layout.addStretch()
        return container

    def _create_group(
        self, title, actions, large=False, source_kind=None, source_name=None
    ):
        """Create a ribbon group: a framed section with buttons and a title."""
        group = QFrame()
        group.setObjectName("ribbonGroup")
        group.setStyleSheet(GROUP_FRAME_STYLE)

        main_layout = QVBoxLayout(group)
        main_layout.setContentsMargins(4, 2, 4, 0)
        main_layout.setSpacing(0)

        if large:
            btn_layout = self._create_large_button_layout(
                actions, source_kind, source_name, group
            )
            main_layout.addLayout(btn_layout)
        else:
            grid = self._create_small_button_grid(
                actions, source_kind, source_name, group
            )
            main_layout.addLayout(grid)

        self._add_group_title(main_layout, title)
        return group

    def _add_group_title(self, main_layout, title):
        """Add the group title at the bottom of a group."""
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(GROUP_TITLE_STYLE)
        main_layout.addWidget(title_label)

    def _create_large_button_layout(self, actions, source_kind, source_name, parent):
        """Create a horizontal layout with large buttons."""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(2)
        for action in actions:
            if action.isSeparator():
                self._add_separator_to_layout(btn_layout)
                continue
            if isinstance(action, QWidgetAction):
                self._add_widget_action_to_layout(
                    btn_layout,
                    action,
                    large=True,
                    source_name=source_name,
                    parent=parent,
                )
                continue
            btn = self._make_button(
                action,
                large=True,
                source_kind=source_kind,
                source_name=source_name,
                parent=parent,
            )
            btn_layout.addWidget(btn)
        return btn_layout

    def _create_small_button_grid(self, actions, source_kind, source_name, parent):
        """Create a grid layout with small buttons (up to 3 rows)."""
        grid = QGridLayout()
        grid.setSpacing(1)
        grid.setContentsMargins(0, 0, 0, 0)
        row, col = 0, 0
        for action in actions:
            if action.isSeparator() and row > 0:
                col += 1
                row = 0
                continue
            if isinstance(action, QWidgetAction):
                row, col = self._add_widget_action_to_grid(
                    grid, action, row, col, source_name=source_name, parent=parent
                )
                continue
            btn = self._make_button(
                action,
                large=False,
                source_kind=source_kind,
                source_name=source_name,
                parent=parent,
            )
            grid.addWidget(btn, row, col)
            row += 1
            if row >= 3:
                row = 0
                col += 1
        return grid

    def _add_separator_to_layout(self, layout):
        """Add a vertical separator line to a layout."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setFixedWidth(1)
        layout.addWidget(sep)

    def _add_widget_action_to_layout(
        self, layout, action, large=False, source_name=None, parent=None
    ):
        """Add a widget action button to a horizontal layout."""
        dw = action.defaultWidget()
        if dw is None:
            return
        btn = self._clone_widget_button(
            dw,
            large=large,
            source_name=source_name,
            parent=parent,
        )
        if btn is None:
            return
        layout.addWidget(btn)

    def _add_widget_action_to_grid(
        self, grid, action, row, col, source_name=None, parent=None
    ):
        """Add a widget action button to a grid layout and return updated row/col."""
        dw = action.defaultWidget()
        if dw is None:
            return row, col
        btn = self._clone_widget_button(
            dw,
            large=False,
            source_name=source_name,
            parent=parent,
        )
        if btn is None:
            return row, col
        grid.addWidget(btn, row, col)
        row += 1
        if row >= 3:
            row = 0
            col += 1
        return row, col

    def _clean_text(self, text):
        return re.sub(r"<[^>]+>", "", (text or "").replace("&", "")).strip()

    def _action_popup_id(self, action):
        return action.objectName() or self._clean_text(action.text())

    def _widget_popup_id(self, source):
        default_action = source.defaultAction()
        if default_action and default_action.objectName():
            return default_action.objectName()
        if default_action and self._clean_text(default_action.text()):
            return self._clean_text(default_action.text())
        if self._clean_text(source.text()):
            return self._clean_text(source.text())
        if self._clean_text(source.toolTip()):
            return self._clean_text(source.toolTip())
        return ""

    def _is_popup_action(self, source_kind, source_name, action):
        action_key = (source_name, self._action_popup_id(action))
        popup_actions = {
            "menu": MENU_POPUP_ACTIONS,
            "toolbar": TOOLBAR_POPUP_ACTIONS,
        }.get(source_kind)
        if not popup_actions:
            return False
        return action_key in popup_actions

    def _is_popup_widget_button(self, source_name, source):
        return (source_name, self._widget_popup_id(source)) in WIDGET_POPUP_BUTTONS

    def _clone_widget_button(
        self,
        source,
        large=False,
        source_name=None,
        parent=None,
        popup=None,
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
        if popup is None:
            popup = self._is_popup_widget_button(source_name, source)
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
        if large:
            clone.setIconSize(QSize(28, 28))
            clone.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            if labeled:
                clone.setFixedHeight(70)
                clone.setMinimumWidth(56)
            else:
                clone.setFixedSize(56, 70)
        elif labeled:
            clone.setIconSize(QSize(18, 18))
            clone.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            clone.setFixedHeight(22)
        else:
            clone.setIconSize(QSize(18, 18))
            if source.icon().isNull():
                clone.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            else:
                clone.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            clone.setFixedHeight(22)
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

    def _make_button(
        self,
        action,
        large=False,
        source_kind=None,
        source_name=None,
        parent=None,
        popup=None,
        labeled=False,
    ):
        """Create a QToolButton for a ribbon action.

        popup: show the action's submenu as a popup (default: looked up in
        the *_POPUP_ACTIONS sets). labeled: always show the full label
        (small buttons get text beside the icon, large ones grow in width).
        """
        btn = QToolButton(parent)
        btn.setAutoRaise(True)

        if popup is None:
            popup = self._is_popup_action(source_kind, source_name, action)
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

        if large:
            btn.setIconSize(QSize(28, 28))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            if labeled:
                btn.setFixedHeight(70)
                btn.setMinimumWidth(56)
            else:
                btn.setFixedSize(56, 70)
        else:
            btn.setIconSize(QSize(18, 18))
            if labeled:
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                if action.icon().isNull():
                    # Blank icon keeps labels aligned with iconed buttons
                    blank = QPixmap(18, 18)
                    blank.fill(Qt.GlobalColor.transparent)
                    btn.setIcon(QIcon(blank))
            elif action.icon() and not action.icon().isNull():
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            else:
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
                btn.setMaximumWidth(120)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(22)

        return btn
