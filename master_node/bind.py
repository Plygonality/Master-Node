"""Walk Blender data into the bpy-free resolver, then write markers back."""

from __future__ import annotations

from typing import Any

import bpy

from master_node.core.protocol import (
    PROP_MASTER,
    Binding,
    MasterRec,
    NodeRec,
    master_props,
    read_master_props,
)
from master_node.core.resolve import resolve_binding


def active_material(context: bpy.types.Context) -> bpy.types.Material | None:
    space = getattr(context, "space_data", None)
    if space is not None and getattr(space, "type", None) == "NODE_EDITOR":
        ident = getattr(space, "id", None)
        if isinstance(ident, bpy.types.Material):
            return ident
    obj = context.object
    if obj is None:
        return None
    return obj.active_material


def iter_shader_groups(ntree: bpy.types.NodeTree | None) -> list[bpy.types.ShaderNodeGroup]:
    if ntree is None:
        return []
    return [n for n in ntree.nodes if n.bl_idname == "ShaderNodeGroup" and n.node_tree]


def collect_masters() -> dict[str, MasterRec]:
    found: dict[str, MasterRec] = {}
    for tree in bpy.data.node_groups:
        if getattr(tree, "type", "") != "SHADER":
            continue
        markers = read_master_props(dict(tree.items()))
        if markers is None:
            continue
        found[tree.name] = MasterRec(
            name=tree.name,
            category=markers["mn.category"],
            origin=markers["mn.origin"],
            version=markers["mn.version"],
        )
    return found


def material_nodes(mat: bpy.types.Material) -> list[NodeRec]:
    ntree = mat.node_tree if mat.use_nodes else None
    if ntree is None:
        return []
    recs: list[NodeRec] = []
    for node in ntree.nodes:
        group = node.node_tree.name if getattr(node, "node_tree", None) else None
        recs.append(NodeRec(name=node.name, bl_idname=node.bl_idname, group=group))
    return recs


def binding_for(mat: bpy.types.Material | None) -> Binding | None:
    if mat is None:
        return None
    marked = mat.get(PROP_MASTER) or None
    if marked is not None:
        marked = str(marked)
    return resolve_binding(mat.name, marked, material_nodes(mat), collect_masters())


def binding_node(
    mat: bpy.types.Material, binding: Binding
) -> bpy.types.ShaderNodeGroup | None:
    ntree = mat.node_tree
    if ntree is None:
        return None
    if binding.node and binding.node in ntree.nodes:
        node = ntree.nodes[binding.node]
        if node.bl_idname == "ShaderNodeGroup":
            return node
    for node in iter_shader_groups(ntree):
        if node.node_tree.name == binding.group:
            return node
    return None


def mark_tree(tree: bpy.types.NodeTree, category: str, *, origin: str = "framework") -> None:
    for key, value in master_props(category, origin=origin).items():  # type: ignore[arg-type]
        tree[key] = value


def mark_material(mat: bpy.types.Material, group_name: str) -> None:
    mat[PROP_MASTER] = group_name


def dump_binding(mat: bpy.types.Material | None) -> dict[str, Any] | None:
    binding = binding_for(mat)
    if binding is None or mat is None:
        return None
    data = binding.to_dict()
    node = binding_node(mat, binding)
    if node is not None:
        data["values"] = socket_values(node)
    return data


def socket_values(node: bpy.types.Node) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for socket in node.inputs:
        if socket.bl_idname == "NodeSocketShader" or not hasattr(socket, "default_value"):
            continue
        values[socket.name] = _rna_to_json(socket.default_value)
    return values


def _rna_to_json(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) if not isinstance(value, int) else value
    if isinstance(value, str):
        return value
    to_list = getattr(value, "to_list", None)
    if callable(to_list):
        return [_rna_to_json(v) for v in to_list()]
    if type(value).__name__ == "bpy_prop_array" or isinstance(value, (tuple, list)):
        return [_rna_to_json(v) for v in value]
    return value
