"""Master-node markers and the bpy-free binding record.

A node group is a category master when it carries ``mn.is_master``.
A material binds to one master by name (``mn.master``) or by walking its tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

FORMAT = "master-node"
FORMAT_VERSION = 1

PROP_IS_MASTER = "mn.is_master"
PROP_CATEGORY = "mn.category"
PROP_VERSION = "mn.version"
PROP_ORIGIN = "mn.origin"
PROP_MASTER = "mn.master"

Origin = Literal["framework", "user"]
Tier = Literal["free", "paid"]

CATEGORIES = (
    "surface",
    "metal",
    "dielectric",
    "glass",
    "fabric",
    "emissive",
    "layered",
)

TREE_PREFIX = "MN "


def tree_name_for(category: str) -> str:
    return f"{TREE_PREFIX}{category.replace('_', ' ').title()}"


def is_known_category(category: str) -> bool:
    return category in CATEGORIES


def master_props(
    category: str,
    *,
    origin: Origin = "framework",
    version: int = FORMAT_VERSION,
) -> dict[str, Any]:
    if not is_known_category(category):
        raise ValueError(f"unknown category: {category}")
    return {
        PROP_IS_MASTER: True,
        PROP_CATEGORY: category,
        PROP_VERSION: int(version),
        PROP_ORIGIN: origin,
    }


def read_master_props(props: dict[str, Any]) -> dict[str, Any] | None:
    """Return normalized master markers, or None if this is not a master."""
    if not props.get(PROP_IS_MASTER):
        return None
    category = str(props.get(PROP_CATEGORY, "")).strip().lower()
    if not category:
        return None
    origin = props.get(PROP_ORIGIN, "user")
    if origin not in ("framework", "user"):
        origin = "user"
    try:
        version = int(props.get(PROP_VERSION, FORMAT_VERSION))
    except (TypeError, ValueError):
        version = FORMAT_VERSION
    return {
        PROP_IS_MASTER: True,
        PROP_CATEGORY: category,
        PROP_VERSION: version,
        PROP_ORIGIN: origin,
    }


@dataclass(frozen=True)
class NodeRec:
    """A material-tree node, enough to resolve a binding without bpy."""

    name: str
    bl_idname: str = "ShaderNodeGroup"
    group: str | None = None


@dataclass(frozen=True)
class MasterRec:
    name: str
    category: str
    origin: Origin = "framework"
    version: int = FORMAT_VERSION


@dataclass(frozen=True)
class Binding:
    """Resolved category master for one material."""

    material: str
    group: str
    category: str
    node: str | None = None
    origin: Origin = "framework"
    version: int = FORMAT_VERSION
    source: Literal["marker", "walk"] = "marker"

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": FORMAT,
            "version": FORMAT_VERSION,
            "material": self.material,
            "group": self.group,
            "category": self.category,
            "node": self.node,
            "origin": self.origin,
            "master_version": self.version,
            "source": self.source,
        }
