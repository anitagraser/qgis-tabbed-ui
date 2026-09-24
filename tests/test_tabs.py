# -*- coding: utf-8 -*-
"""Checks for the tab configuration (runs without QGIS)."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_DIR / "qgis_tabbed_ui"
sys.path.insert(0, str(REPO_DIR))

from qgis_tabbed_ui import tabs  # noqa: E402
from qgis_tabbed_ui.tabs.spec import ArrangedTab, MenuTab, ToolbarTab  # noqa: E402


def test_icon_overrides_exist():
    for name, icon in tabs.ICON_OVERRIDES.items():
        if not icon.startswith(":"):
            assert (PLUGIN_DIR / "icons" / icon).is_file(), name


def test_metadata_icon_exists():
    metadata = (PLUGIN_DIR / "metadata.txt").read_text()
    icon = next(
        line.split("=", 1)[1].strip()
        for line in metadata.splitlines()
        if line.startswith("icon=")
    )
    assert (PLUGIN_DIR / icon).is_file()


def test_every_tab_module_defines_a_tab():
    for module in tabs.TAB_MODULES:
        assert isinstance(module.TAB, (ArrangedTab, MenuTab, ToolbarTab)), module


def test_one_default_tab():
    assert len([spec for spec in tabs.TABS if spec.default]) == 1


def test_merge_rejects_duplicate_keys():
    a = SimpleNamespace(__name__="a", SHORT_LABELS={"mActionPan": "Pan"})
    b = SimpleNamespace(__name__="b", SHORT_LABELS={"mActionPan": "Move"})
    with pytest.raises(ValueError, match="mActionPan"):
        tabs._merge("SHORT_LABELS", modules=[a, b])


def test_merge_combines_sets():
    a = SimpleNamespace(__name__="a", ICON_ONLY={"x", "y"})
    b = SimpleNamespace(__name__="b", ICON_ONLY={"y", "z"})
    assert tabs._merge("ICON_ONLY", set, modules=[a, b]) == {"x", "y", "z"}
