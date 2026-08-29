"""Operators: create / bind / mark / apply preset / set a socket."""

from __future__ import annotations

import json

import bpy
from bpy.props import StringProperty

from master_node.assign import assign_category, ensure_object_material
from master_node.bind import active_material, binding_for, binding_node, mark_material, mark_tree
from master_node.core.presets import apply_values
from master_node.core.protocol import is_known_category
from master_node.prefs import license_key, paid_pack_dir
from master_node.rna_draw import apply_socket_map, set_socket_value
from master_node.store import preset_by_id


class MASTERNODE_OT_create(bpy.types.Operator):
    bl_idname = "master_node.create"
    bl_label = "Create Master"
    bl_description = "Create the category master and bind it to the active material"
    bl_options = {"REGISTER", "UNDO"}

    category: StringProperty(name="Category", default="surface")

    def execute(self, context):
        if not is_known_category(self.category):
            self.report({"ERROR"}, f"Unknown category: {self.category}")
            return {"CANCELLED"}
        obj = context.object
        if obj is None:
            self.report({"ERROR"}, "Select an object")
            return {"CANCELLED"}
        mat = ensure_object_material(obj)
        assign_category(mat, self.category)
        self.report({"INFO"}, f"Bound {mat.name} → MN {self.category.title()}")
        return {"FINISHED"}


class MASTERNODE_OT_bind_selected(bpy.types.Operator):
    bl_idname = "master_node.bind_selected"
    bl_label = "Bind Selected Group"
    bl_description = "Mark the selected shader group as this material's category master"
    bl_options = {"REGISTER", "UNDO"}

    category: StringProperty(name="Category", default="surface")

    def execute(self, context):
        mat = active_material(context)
        space = getattr(context, "space_data", None)
        ntree = getattr(space, "node_tree", None) if space else None
        if mat is None or ntree is None:
            self.report({"ERROR"}, "Open the Shader Editor on a material")
            return {"CANCELLED"}
        selected = [n for n in ntree.nodes if n.select and n.bl_idname == "ShaderNodeGroup" and n.node_tree]
        if not selected:
            self.report({"ERROR"}, "Select a node group")
            return {"CANCELLED"}
        node = selected[0]
        if not is_known_category(self.category):
            self.report({"ERROR"}, f"Unknown category: {self.category}")
            return {"CANCELLED"}
        mark_tree(node.node_tree, self.category, origin="user")
        mark_material(mat, node.node_tree.name)
        self.report({"INFO"}, f"Bound {mat.name} → {node.node_tree.name}")
        return {"FINISHED"}


class MASTERNODE_OT_select_master(bpy.types.Operator):
    bl_idname = "master_node.select_master"
    bl_label = "Select Master"
    bl_description = "Select the bound master group in the material node tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = active_material(context)
        binding = binding_for(mat)
        if mat is None or binding is None:
            self.report({"ERROR"}, "No bound master")
            return {"CANCELLED"}
        node = binding_node(mat, binding)
        ntree = mat.node_tree
        if node is None or ntree is None:
            self.report({"ERROR"}, "Master instance not found")
            return {"CANCELLED"}
        for other in ntree.nodes:
            other.select = other == node
        ntree.nodes.active = node
        return {"FINISHED"}


class MASTERNODE_OT_apply_preset(bpy.types.Operator):
    bl_idname = "master_node.apply_preset"
    bl_label = "Apply Preset"
    bl_description = "Write a preset's values onto the bound master via RNA"
    bl_options = {"REGISTER", "UNDO"}

    preset_id: StringProperty(name="Preset")

    def execute(self, context):
        mat = active_material(context)
        binding = binding_for(mat)
        if mat is None or binding is None:
            self.report({"ERROR"}, "No bound master")
            return {"CANCELLED"}
        preset = preset_by_id(self.preset_id, paid_pack_dir(context))
        if preset is None:
            self.report({"ERROR"}, f"Unknown preset: {self.preset_id}")
            return {"CANCELLED"}
        if preset.category != binding.category:
            self.report({"ERROR"}, f"Preset is {preset.category}, master is {binding.category}")
            return {"CANCELLED"}
        try:
            values = apply_values(preset, license_key(context))
        except PermissionError:
            self.report({"ERROR"}, "Paid preset — add a license key in Preferences")
            return {"CANCELLED"}
        node = binding_node(mat, binding)
        if node is None:
            self.report({"ERROR"}, "Master instance not found")
            return {"CANCELLED"}
        skipped = apply_socket_map(node, values, category=binding.category)
        msg = f"Applied {preset.name}"
        if skipped:
            msg += f" (skipped {len(skipped)})"
        self.report({"INFO"}, msg)
        return {"FINISHED"}


class MASTERNODE_OT_set_param(bpy.types.Operator):
    bl_idname = "master_node.set_param"
    bl_label = "Set Parameter"
    bl_description = "Set one bound-master socket. Value is JSON. For the agent loop."
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Socket")
    value: StringProperty(name="Value", description="JSON number, bool, or array")

    def execute(self, context):
        mat = active_material(context)
        binding = binding_for(mat)
        if mat is None or binding is None:
            self.report({"ERROR"}, "No bound master")
            return {"CANCELLED"}
        node = binding_node(mat, binding)
        if node is None:
            self.report({"ERROR"}, "Master instance not found")
            return {"CANCELLED"}
        try:
            parsed = json.loads(self.value)
        except json.JSONDecodeError as exc:
            self.report({"ERROR"}, f"Invalid JSON: {exc}")
            return {"CANCELLED"}
        try:
            set_socket_value(node, self.name, parsed)
        except (KeyError, TypeError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


CLASSES = (
    MASTERNODE_OT_create,
    MASTERNODE_OT_bind_selected,
    MASTERNODE_OT_select_master,
    MASTERNODE_OT_apply_preset,
    MASTERNODE_OT_set_param,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
