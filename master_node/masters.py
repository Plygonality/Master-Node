"""Build framework category masters from the catalog.

The catalog is the source of truth. This module only instantiates ShaderNodeTree
datablocks and wires them to Principled BSDF.
"""

from __future__ import annotations

import bpy

from master_node.bind import mark_tree
from master_node.core.catalog import CategorySpec, SocketSpec, get_category
from master_node.core.protocol import PROP_IS_MASTER, read_master_props, tree_name_for

_SOCKET_BL = {
    "FLOAT": "NodeSocketFloat",
    "COLOR": "NodeSocketColor",
    "VECTOR": "NodeSocketVector",
    "INT": "NodeSocketInt",
    "BOOL": "NodeSocketBool",
}


def find_framework_master(category: str) -> bpy.types.NodeTree | None:
    expected = tree_name_for(category)
    tree = bpy.data.node_groups.get(expected)
    if tree is not None and tree.get(PROP_IS_MASTER):
        return tree
    for candidate in bpy.data.node_groups:
        markers = read_master_props(dict(candidate.items()))
        if markers and markers["mn.category"] == category and markers["mn.origin"] == "framework":
            return candidate
    return None


def ensure_master(category: str) -> bpy.types.NodeTree:
    existing = find_framework_master(category)
    if existing is not None:
        return existing
    return build_master(category)


def build_master(category: str) -> bpy.types.NodeTree:
    spec = get_category(category)
    name = spec.tree_name
    if name in bpy.data.node_groups:
        tree = bpy.data.node_groups[name]
        bpy.data.node_groups.remove(tree)
    tree = bpy.data.node_groups.new(name, "ShaderNodeTree")
    mark_tree(tree, spec.id, origin="framework")
    _build_interface(tree, spec)
    _build_graph(tree, spec)
    return tree


def rebuild_master(category: str) -> bpy.types.NodeTree:
    return build_master(category)


def _build_interface(tree: bpy.types.NodeTree, spec: CategorySpec) -> None:
    interface = tree.interface
    panels: dict[str, object] = {}
    for panel_name in spec.panels():
        panels[panel_name] = interface.new_panel(name=panel_name)
    for socket in spec.sockets:
        kwargs = {}
        if socket.panel and socket.panel in panels:
            kwargs["parent"] = panels[socket.panel]
        item = interface.new_socket(
            socket.name,
            in_out="INPUT",
            socket_type=_SOCKET_BL[socket.socket],
            **kwargs,
        )
        _apply_socket_defaults(item, socket)
    interface.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")


def _apply_socket_defaults(item, socket: SocketSpec) -> None:
    if socket.default is not None and hasattr(item, "default_value"):
        item.default_value = socket.default
    if socket.subtype and hasattr(item, "subtype"):
        try:
            item.subtype = socket.subtype
        except TypeError:
            pass
    if socket.min is not None and hasattr(item, "min_value"):
        item.min_value = socket.min
    if socket.max is not None and hasattr(item, "max_value"):
        item.max_value = socket.max
    if socket.description and hasattr(item, "description"):
        item.description = socket.description


def _build_graph(tree: bpy.types.NodeTree, spec: CategorySpec) -> None:
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-360, 0)
    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (360, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.label = spec.label

    for name, value in spec.constants.items():
        if name in bsdf.inputs:
            _safe_set(bsdf.inputs[name], value)

    for master_name, principled_name in spec.principled_map.items():
        src = group_in.outputs.get(master_name)
        dst = bsdf.inputs.get(principled_name)
        if src is None or dst is None:
            continue
        links.new(src, dst)

    out_bsdf = group_out.inputs.get("BSDF")
    if out_bsdf is not None and "BSDF" in bsdf.outputs:
        links.new(bsdf.outputs["BSDF"], out_bsdf)


def _safe_set(socket, value) -> None:
    try:
        socket.default_value = value
    except (TypeError, ValueError):
        if hasattr(value, "__iter__") and not isinstance(value, str):
            try:
                socket.default_value = list(value)
            except (TypeError, ValueError):
                pass
