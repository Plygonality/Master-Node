"""bpy-free master-node protocol.

The add-on is the product artists install. This package is the source of truth
for markers, category interfaces, presets, and the paid gate. Tests run here
without opening Blender.
"""

from master_node.core.catalog import (
    CATALOG,
    CategorySpec,
    SocketSpec,
    get_category,
    validate_catalog,
)
from master_node.core.license import DEV_UNLOCK, can_apply, is_unlocked
from master_node.core.presets import Preset, PresetError, from_dict, listings_for, validate_preset
from master_node.core.protocol import (
    CATEGORIES,
    FORMAT,
    FORMAT_VERSION,
    PROP_CATEGORY,
    PROP_IS_MASTER,
    PROP_MASTER,
    PROP_ORIGIN,
    PROP_VERSION,
    Binding,
    MasterRec,
    NodeRec,
    master_props,
    read_master_props,
    tree_name_for,
)
from master_node.core.resolve import resolve_binding

__all__ = [
    "CATALOG",
    "CATEGORIES",
    "DEV_UNLOCK",
    "FORMAT",
    "FORMAT_VERSION",
    "PROP_CATEGORY",
    "PROP_IS_MASTER",
    "PROP_MASTER",
    "PROP_ORIGIN",
    "PROP_VERSION",
    "Binding",
    "CategorySpec",
    "MasterRec",
    "NodeRec",
    "Preset",
    "PresetError",
    "SocketSpec",
    "can_apply",
    "from_dict",
    "get_category",
    "is_unlocked",
    "listings_for",
    "master_props",
    "read_master_props",
    "resolve_binding",
    "tree_name_for",
    "validate_catalog",
    "validate_preset",
]

__version__ = "0.1.0"
