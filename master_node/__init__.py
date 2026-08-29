# SPDX-License-Identifier: MIT
"""Master Node — category masters in the N-panel.

This is the material-system product. The framework is public. Presets are paid.
Artists install the add-on. They do not need Cursor or MCP.

Importing this package does not require bpy — ``core`` is the source of truth
and the tests run against it. ``register()`` is the Blender entry point.
"""

from __future__ import annotations

bl_info = {
    "name": "Master Node",
    "author": "Plygon",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Master Node",
    "description": "N-panel that binds to a category master node and exposes its parameters",
    "category": "Material",
    "doc_url": "https://github.com/Plygonality/Master-Node",
}

__version__ = "0.1.0"


def register():
    from . import ops, panel, prefs

    prefs.register()
    ops.register()
    panel.register()


def unregister():
    from . import ops, panel, prefs

    panel.unregister()
    ops.unregister()
    prefs.unregister()
