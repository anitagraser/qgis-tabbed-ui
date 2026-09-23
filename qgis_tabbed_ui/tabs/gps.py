# -*- coding: utf-8 -*-
"""GPS tab: the GPS toolbar."""

from .spec import ToolbarTab

TAB = ToolbarTab(title="GPS", toolbars=[("mGpsToolBar", None)])

TOOLBAR_GROUP_OPTIONS = {
    "mGpsToolBar": {"rows": 2, "icon_size": 24, "large": ["mConnectAction"]},
}
