"""N-panel: bind to the category master and draw its RNA sockets."""

from __future__ import annotations

import bpy

from master_node.bind import active_material, binding_for, binding_node
from master_node.core.catalog import get_category
from master_node.prefs import license_key, paid_pack_dir
from master_node.rna_draw import draw_master
from master_node.store import panel_listings

TAB = "Master Node"


class MASTERNODE_PT_base(bpy.types.Panel):
    bl_label = "Master Node"
    bl_region_type = "UI"
    bl_category = TAB

    def draw_header(self, _context):
        self.layout.label(text="", icon="NODETREE")

    def draw(self, context):
        layout = self.layout
        mat = active_material(context)
        props = getattr(context.scene, "master_node", None)
        if mat is None:
            layout.label(text="Select an object with a material.")
            _draw_create(layout, props)
            return

        binding = binding_for(mat)
        _draw_binding(layout, mat, binding, props)
        if binding is None:
            layout.separator()
            _draw_create(layout, props)
            return

        node = binding_node(mat, binding)
        if node is None:
            layout.label(text="Master is marked but not instanced.")
            _draw_create(layout, props)
            return

        layout.separator()
        box = layout.box()
        box.label(text="Parameters")
        show_linked = bool(props.show_linked) if props else False
        draw_master(box, node, binding.category, show_linked=show_linked)
        if props:
            box.prop(props, "show_linked")

        layout.separator()
        _draw_presets(layout, binding.category, license_key(context), paid_pack_dir(context))


def _draw_binding(layout, mat, binding, props) -> None:
    box = layout.box()
    box.label(text=mat.name, icon="MATERIAL")
    if binding is None:
        box.label(text="No category master bound.")
        return
    try:
        label = get_category(binding.category).label
    except KeyError:
        label = binding.category
    box.label(text=f"{label}  ·  {binding.group}")
    row = box.row(align=True)
    row.operator("master_node.select_master", icon="RESTRICT_SELECT_OFF")
    if props:
        op = row.operator("master_node.create", text="Switch")
        op.category = props.category


def _draw_create(layout, props) -> None:
    if props is None:
        return
    col = layout.column(align=True)
    col.prop(props, "category", text="Category")
    op = col.operator("master_node.create", icon="ADD")
    op.category = props.category
    bind = col.operator("master_node.bind_selected", icon="LINKED")
    bind.category = props.category


def _draw_presets(layout, category: str, key: str, pack_dir: str) -> None:
    box = layout.box()
    box.label(text="Presets")
    listings = panel_listings(category, key, pack_dir)
    if not listings:
        box.label(text="No presets for this category.")
        return
    for listing in listings:
        row = box.row(align=True)
        if listing.locked:
            row.enabled = False
            row.label(text=listing.name, icon="LOCKED")
            continue
        op = row.operator("master_node.apply_preset", text=listing.name)
        op.preset_id = listing.id


class MASTERNODE_PT_view3d(MASTERNODE_PT_base):
    bl_space_type = "VIEW_3D"
    bl_idname = "MASTERNODE_PT_view3d"


class MASTERNODE_PT_shader(MASTERNODE_PT_base):
    bl_space_type = "NODE_EDITOR"
    bl_idname = "MASTERNODE_PT_shader"

    @classmethod
    def poll(cls, context):
        space = getattr(context, "space_data", None)
        return space is not None and getattr(space, "tree_type", None) == "ShaderNodeTree"


CLASSES = (MASTERNODE_PT_view3d, MASTERNODE_PT_shader)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
