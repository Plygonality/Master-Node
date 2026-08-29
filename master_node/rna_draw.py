"""Draw a bound master node's sockets through RNA.

``layout.prop(socket, "default_value")`` is the path. Sliders, color pickers,
and animation all come from the socket — the panel does not invent properties.
"""

from __future__ import annotations

from collections.abc import Iterable

import bpy

from master_node.core.catalog import CATALOG, SocketSpec, get_category


def draw_master(
    layout: bpy.types.UILayout,
    node: bpy.types.Node,
    category: str,
    *,
    show_linked: bool = False,
) -> None:
    spec = CATALOG.get(category)
    if spec is None:
        _draw_unknown(layout, node, show_linked=show_linked)
        return

    leftovers = {s.name for s in spec.sockets}
    _draw_group(layout, node, spec.sockets_in(""), leftovers, show_linked=show_linked)
    for panel_name in spec.panels():
        box = layout.box()
        box.label(text=panel_name)
        _draw_group(box, node, spec.sockets_in(panel_name), leftovers, show_linked=show_linked)
    extra = [s for s in node.inputs if s.name in leftovers or s.name not in spec.socket_map()]
    extra = [s for s in extra if s.bl_idname != "NodeSocketShader"]
    if extra:
        box = layout.box()
        box.label(text="Other")
        for socket in extra:
            leftovers.discard(socket.name)
            _draw_socket(box, socket, show_linked=show_linked)


def _draw_group(
    layout: bpy.types.UILayout,
    node: bpy.types.Node,
    sockets: Iterable[SocketSpec],
    leftovers: set[str],
    *,
    show_linked: bool,
) -> None:
    col = layout.column(align=True)
    for spec in sockets:
        leftovers.discard(spec.name)
        socket = node.inputs.get(spec.name)
        if socket is None:
            continue
        _draw_socket(col, socket, show_linked=show_linked)


def _draw_unknown(layout: bpy.types.UILayout, node: bpy.types.Node, *, show_linked: bool) -> None:
    col = layout.column(align=True)
    for socket in node.inputs:
        if socket.bl_idname == "NodeSocketShader":
            continue
        _draw_socket(col, socket, show_linked=show_linked)


def _draw_socket(layout: bpy.types.UILayout, socket: bpy.types.NodeSocket, *, show_linked: bool) -> None:
    if not hasattr(socket, "default_value"):
        return
    if socket.is_linked and not show_linked:
        row = layout.row()
        row.enabled = False
        row.label(text=f"{socket.name}  (linked)")
        return
    layout.prop(socket, "default_value", text=socket.name)


def set_socket_value(node: bpy.types.Node, name: str, value) -> None:
    """Write a value onto a group-node input via RNA ``default_value``."""
    socket = node.inputs.get(name)
    if socket is None:
        raise KeyError(f"no socket {name!r} on {node.name}")
    if socket.bl_idname == "NodeSocketShader" or not hasattr(socket, "default_value"):
        raise TypeError(f"socket {name!r} has no default_value")
    socket.default_value = _coerce(socket, value)


def _coerce(socket: bpy.types.NodeSocket, value):
    identifier = socket.bl_idname
    if identifier in {"NodeSocketColor", "NodeSocketVector"}:
        seq = list(value)
        current = list(socket.default_value)
        if identifier == "NodeSocketColor":
            if len(seq) == 3:
                seq = seq + [1.0]
            return seq[:4]
        return (seq + current)[: len(current)]
    if identifier == "NodeSocketBool":
        return bool(value)
    if identifier == "NodeSocketInt":
        return int(value)
    return float(value)


def apply_socket_map(node: bpy.types.Node, values: dict, *, category: str | None = None) -> list[str]:
    """Write a preset map. Unknown names are skipped and returned."""
    skipped: list[str] = []
    allowed = None
    if category:
        allowed = set(get_category(category).socket_map())
    for name, value in values.items():
        if allowed is not None and name not in allowed:
            skipped.append(name)
            continue
        if name not in node.inputs:
            skipped.append(name)
            continue
        try:
            set_socket_value(node, name, value)
        except (KeyError, TypeError, ValueError):
            skipped.append(name)
    return skipped
