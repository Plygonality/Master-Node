"""Agent-facing helpers for the live Blender loop.

Plygon-mcp (or ``blender -P``) imports this and: bind a category, tweak a
slider through RNA, dump the binding. The product itself is the add-on —
artists never need this module.
"""

from __future__ import annotations

from typing import Any

import bpy

from master_node.assign import assign_category, ensure_object_material
from master_node.bind import binding_for, binding_node, dump_binding
from master_node.rna_draw import set_socket_value


def active_object(context: bpy.types.Context | None = None) -> bpy.types.Object:
    ctx = context or bpy.context
    obj = ctx.object
    if obj is None:
        raise RuntimeError("no active object")
    return obj


def bind_category(category: str = "metal", context: bpy.types.Context | None = None) -> dict[str, Any]:
    ctx = context or bpy.context
    obj = active_object(ctx)
    mat = ensure_object_material(obj)
    assign_category(mat, category)
    dump = dump_binding(mat)
    assert dump is not None
    return dump


def set_param(name: str, value, context: bpy.types.Context | None = None) -> dict[str, Any]:
    ctx = context or bpy.context
    obj = active_object(ctx)
    mat = obj.active_material
    binding = binding_for(mat)
    if mat is None or binding is None:
        raise RuntimeError("no bound master")
    node = binding_node(mat, binding)
    if node is None:
        raise RuntimeError("master instance not found")
    set_socket_value(node, name, value)
    dump = dump_binding(mat)
    assert dump is not None
    return dump


def get_binding(context: bpy.types.Context | None = None) -> dict[str, Any] | None:
    ctx = context or bpy.context
    obj = ctx.object
    if obj is None:
        return None
    return dump_binding(obj.active_material)
