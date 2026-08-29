"""Add-on preferences and scene-level panel state."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty

from master_node.core.catalog import category_items
from master_node.core.license import DEV_UNLOCK, is_unlocked

_CATEGORY_ITEMS = tuple((ident, label, desc) for ident, label, desc in category_items())


class MASTERNODE_AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    license_key: StringProperty(
        name="License key",
        description="Unlocks paid preset packs. The framework does not need a key",
        default="",
        subtype="PASSWORD",
    )
    paid_pack_dir: StringProperty(
        name="Paid pack folder",
        description="Optional folder of paid preset JSON files",
        default="",
        subtype="DIR_PATH",
    )

    def draw(self, _context):
        layout = self.layout
        layout.prop(self, "license_key")
        status = "Unlocked" if is_unlocked(self.license_key) else "Framework only — presets stay free"
        layout.label(text=status)
        layout.prop(self, "paid_pack_dir")
        box = layout.box()
        box.label(text="Dev unlock (tests / Plygon-mcp loop)")
        box.label(text=DEV_UNLOCK, translate=False)


class MASTERNODE_SceneProps(bpy.types.PropertyGroup):
    category: EnumProperty(
        name="Category",
        description="Category master to create or switch to",
        items=_CATEGORY_ITEMS,
        default="surface",
    )
    show_linked: BoolProperty(
        name="Show linked",
        description="Draw sockets that are already driven by another node",
        default=False,
    )


def addon_prefs(context: bpy.types.Context | None = None) -> MASTERNODE_AddonPrefs | None:
    ctx = context or bpy.context
    addon = ctx.preferences.addons.get(__package__)
    if addon is None:
        return None
    return addon.preferences


def license_key(context: bpy.types.Context | None = None) -> str:
    prefs = addon_prefs(context)
    return prefs.license_key if prefs else ""


def paid_pack_dir(context: bpy.types.Context | None = None) -> str:
    prefs = addon_prefs(context)
    return prefs.paid_pack_dir if prefs else ""


CLASSES = (MASTERNODE_AddonPrefs, MASTERNODE_SceneProps)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.master_node = bpy.props.PointerProperty(type=MASTERNODE_SceneProps)


def unregister():
    if hasattr(bpy.types.Scene, "master_node"):
        del bpy.types.Scene.master_node
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
