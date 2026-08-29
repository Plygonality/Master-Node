"""Self-contained bpy script for the live Blender loop.

Plygon-mcp: execute_blender_code(this) → get_viewport_screenshot().

Binds a metal master on the active object (or a cube), sets Roughness
through RNA, returns the binding dump.
"""

from __future__ import annotations

import bpy


def _ensure_object():
    obj = bpy.context.object
    if obj is not None and obj.type == "MESH":
        return obj
    bpy.ops.mesh.primitive_cube_add()
    return bpy.context.object


def run() -> dict:
    _ensure_object()
    from master_node import live

    dump = live.bind_category("metal")
    dump = live.set_param("Roughness", 0.12)
    dump = live.set_param("Color", [0.85, 0.86, 0.88, 1.0])
    return dump


if __name__ == "__main__":
    result = run()
    print(result)
