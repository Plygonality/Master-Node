"""Put a category master on a material and keep the binding marker in sync."""

from __future__ import annotations

import bpy

from master_node.bind import mark_material
from master_node.core.protocol import tree_name_for
from master_node.masters import ensure_master


def ensure_object_material(obj: bpy.types.Object, name: str | None = None) -> bpy.types.Material:
    if obj.active_material is not None:
        return obj.active_material
    mat = bpy.data.materials.new(name or f"{obj.name} Material")
    mat.use_nodes = True
    if obj.data is not None and hasattr(obj.data, "materials"):
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    else:
        obj.active_material = mat
    return mat


def assign_category(mat: bpy.types.Material, category: str) -> bpy.types.ShaderNodeGroup:
    tree = ensure_master(category)
    mat.use_nodes = True
    ntree = mat.node_tree
    assert ntree is not None
    output = _material_output(ntree)
    group = _existing_master_instance(ntree) or ntree.nodes.new("ShaderNodeGroup")
    group.node_tree = tree
    group.name = tree.name
    group.label = tree_name_for(category)
    group.location = (output.location.x - 280, output.location.y)
    _connect_surface(ntree, group, output)
    mark_material(mat, tree.name)
    return group


def _material_output(ntree: bpy.types.NodeTree) -> bpy.types.Node:
    for node in ntree.nodes:
        if node.bl_idname == "ShaderNodeOutputMaterial":
            return node
    node = ntree.nodes.new("ShaderNodeOutputMaterial")
    node.location = (300, 0)
    return node


def _existing_master_instance(ntree: bpy.types.NodeTree) -> bpy.types.ShaderNodeGroup | None:
    from master_node.bind import collect_masters

    masters = collect_masters()
    for node in ntree.nodes:
        if node.bl_idname != "ShaderNodeGroup" or node.node_tree is None:
            continue
        if node.node_tree.name in masters:
            return node
    return None


def _connect_surface(
    ntree: bpy.types.NodeTree, group: bpy.types.Node, output: bpy.types.Node
) -> None:
    surface = output.inputs.get("Surface")
    bsdf = group.outputs.get("BSDF")
    if surface is None or bsdf is None:
        return
    for link in list(surface.links):
        ntree.links.remove(link)
    ntree.links.new(bsdf, surface)
