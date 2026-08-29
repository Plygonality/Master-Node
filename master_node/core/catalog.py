"""Category masters: the public material-system interface.

Each category is one node group. The N-panel draws that group's sockets.
Presets are value packs against these interfaces — they are not the product.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from master_node.core.protocol import CATEGORIES, tree_name_for

SocketKind = str


@dataclass(frozen=True)
class SocketSpec:
    name: str
    socket: SocketKind
    default: Any
    min: float | None = None
    max: float | None = None
    subtype: str = ""
    panel: str = ""
    description: str = ""


@dataclass(frozen=True)
class CategorySpec:
    id: str
    label: str
    description: str
    icon: str
    sockets: tuple[SocketSpec, ...]
    principled_map: dict[str, str]
    constants: dict[str, Any]

    @property
    def tree_name(self) -> str:
        return tree_name_for(self.id)

    def socket_map(self) -> dict[str, SocketSpec]:
        return {s.name: s for s in self.sockets}

    def panels(self) -> tuple[str, ...]:
        seen: list[str] = []
        for spec in self.sockets:
            if spec.panel and spec.panel not in seen:
                seen.append(spec.panel)
        return tuple(seen)

    def sockets_in(self, panel: str) -> tuple[SocketSpec, ...]:
        return tuple(s for s in self.sockets if s.panel == panel)


def _float(
    name: str,
    default: float,
    *,
    min: float = 0.0,
    max: float = 1.0,
    subtype: str = "FACTOR",
    panel: str = "",
    description: str = "",
) -> SocketSpec:
    return SocketSpec(
        name,
        "FLOAT",
        default,
        min=min,
        max=max,
        subtype=subtype,
        panel=panel,
        description=description,
    )


def _color(
    name: str,
    default: tuple[float, float, float, float],
    *,
    panel: str = "",
    description: str = "",
) -> SocketSpec:
    return SocketSpec(name, "COLOR", list(default), panel=panel, description=description)


SURFACE = CategorySpec(
    id="surface",
    label="Surface",
    description="General Principled surface. Start here when the category is not yet decided.",
    icon="MATERIAL",
    sockets=(
        _color("Base Color", (0.8, 0.8, 0.8, 1.0), description="Albedo"),
        _float("Metallic", 0.0, description="Dielectric to metal"),
        _float("Roughness", 0.4, description="Micro-surface roughness"),
        _float("IOR", 1.5, min=1.0, max=2.5, subtype="", description="Index of refraction"),
        _color("Emission Color", (0.0, 0.0, 0.0, 1.0), panel="Emission"),
        _float("Emission Strength", 0.0, min=0.0, max=50.0, subtype="", panel="Emission"),
        _float("Alpha", 1.0, panel="Alpha"),
    ),
    principled_map={
        "Base Color": "Base Color",
        "Metallic": "Metallic",
        "Roughness": "Roughness",
        "IOR": "IOR",
        "Emission Color": "Emission Color",
        "Emission Strength": "Emission Strength",
        "Alpha": "Alpha",
    },
    constants={},
)

METAL = CategorySpec(
    id="metal",
    label="Metal",
    description="Conductor. Metallic is locked on. Color is the F0 reflectance.",
    icon="MESH_CUBE",
    sockets=(
        _color("Color", (0.72, 0.72, 0.74, 1.0), description="F0 / reflectance"),
        _float("Roughness", 0.25, description="Brush, polish, grit"),
        _float("Anisotropy", 0.0, description="Brushed-metal stretch"),
        _float("Rotation", 0.0, description="Anisotropic tangent rotation"),
        _float("Coat Weight", 0.0, panel="Coat"),
        _float("Coat Roughness", 0.03, panel="Coat"),
    ),
    principled_map={
        "Color": "Base Color",
        "Roughness": "Roughness",
        "Anisotropy": "Anisotropic",
        "Rotation": "Anisotropic Rotation",
        "Coat Weight": "Coat Weight",
        "Coat Roughness": "Coat Roughness",
    },
    constants={"Metallic": 1.0, "Specular IOR Level": 1.0},
)

DIELECTRIC = CategorySpec(
    id="dielectric",
    label="Dielectric",
    description="Plastic, rubber, ceramic, painted non-metal.",
    icon="SPHERE",
    sockets=(
        _color("Color", (0.18, 0.18, 0.2, 1.0)),
        _float("Roughness", 0.45),
        _float("Specular", 0.5, description="Specular IOR level"),
        _float("IOR", 1.45, min=1.0, max=2.5, subtype=""),
        _float("Coat Weight", 0.0, panel="Coat"),
        _float("Coat Roughness", 0.05, panel="Coat"),
        _float("Sheen Weight", 0.0, panel="Sheen"),
        _color("Sheen Tint", (1.0, 1.0, 1.0, 1.0), panel="Sheen"),
    ),
    principled_map={
        "Color": "Base Color",
        "Roughness": "Roughness",
        "Specular": "Specular IOR Level",
        "IOR": "IOR",
        "Coat Weight": "Coat Weight",
        "Coat Roughness": "Coat Roughness",
        "Sheen Weight": "Sheen Weight",
        "Sheen Tint": "Sheen Tint",
    },
    constants={"Metallic": 0.0},
)

GLASS = CategorySpec(
    id="glass",
    label="Glass",
    description="Transmissive dielectric. Thin or solid, depending on the mesh.",
    icon="MESH_UVSPHERE",
    sockets=(
        _color("Color", (1.0, 1.0, 1.0, 1.0), description="Absorption / tint"),
        _float("Roughness", 0.0, description="Frost"),
        _float("IOR", 1.45, min=1.0, max=2.5, subtype=""),
        _float("Transmission", 1.0, description="How much light passes through"),
    ),
    principled_map={
        "Color": "Base Color",
        "Roughness": "Roughness",
        "IOR": "IOR",
        "Transmission": "Transmission Weight",
    },
    constants={"Metallic": 0.0, "Alpha": 1.0},
)

FABRIC = CategorySpec(
    id="fabric",
    label="Fabric",
    description="Cloth and soft goods. Sheen does the grazing lift.",
    icon="TEXTURE",
    sockets=(
        _color("Color", (0.35, 0.22, 0.18, 1.0)),
        _float("Roughness", 0.7),
        _float("Sheen Weight", 0.6, panel="Sheen"),
        _float("Sheen Roughness", 0.4, panel="Sheen"),
        _color("Sheen Tint", (0.95, 0.9, 0.85, 1.0), panel="Sheen"),
        _float("Subsurface", 0.05, panel="Volume", description="Thin-cloth scatter"),
    ),
    principled_map={
        "Color": "Base Color",
        "Roughness": "Roughness",
        "Sheen Weight": "Sheen Weight",
        "Sheen Roughness": "Sheen Roughness",
        "Sheen Tint": "Sheen Tint",
        "Subsurface": "Subsurface Weight",
    },
    constants={"Metallic": 0.0, "Specular IOR Level": 0.3},
)

EMISSIVE = CategorySpec(
    id="emissive",
    label="Emissive",
    description="Lights, screens, neon. Base surface stays dark.",
    icon="LIGHT",
    sockets=(
        _color("Color", (1.0, 0.85, 0.55, 1.0)),
        _float("Strength", 8.0, min=0.0, max=200.0, subtype=""),
        _float("Surface Roughness", 0.4, panel="Surface"),
        _color("Surface Color", (0.0, 0.0, 0.0, 1.0), panel="Surface"),
    ),
    principled_map={
        "Color": "Emission Color",
        "Strength": "Emission Strength",
        "Surface Roughness": "Roughness",
        "Surface Color": "Base Color",
    },
    constants={"Metallic": 0.0},
)

LAYERED = CategorySpec(
    id="layered",
    label="Layered",
    description="Clear coat over a base. Car paint, lacquer, wet look.",
    icon="NODE_MATERIAL",
    sockets=(
        _color("Base Color", (0.05, 0.12, 0.35, 1.0)),
        _float("Base Roughness", 0.35),
        _float("Metallic", 0.15),
        _float("Coat Weight", 1.0, panel="Coat"),
        _float("Coat Roughness", 0.03, panel="Coat"),
        _float("Coat IOR", 1.5, min=1.0, max=2.5, subtype="", panel="Coat"),
        _color("Coat Tint", (1.0, 1.0, 1.0, 1.0), panel="Coat"),
    ),
    principled_map={
        "Base Color": "Base Color",
        "Base Roughness": "Roughness",
        "Metallic": "Metallic",
        "Coat Weight": "Coat Weight",
        "Coat Roughness": "Coat Roughness",
        "Coat IOR": "Coat IOR",
        "Coat Tint": "Coat Tint",
    },
    constants={},
)

CATALOG: dict[str, CategorySpec] = {
    spec.id: spec
    for spec in (SURFACE, METAL, DIELECTRIC, GLASS, FABRIC, EMISSIVE, LAYERED)
}


def get_category(category: str) -> CategorySpec:
    try:
        return CATALOG[category]
    except KeyError as exc:
        raise KeyError(f"unknown category: {category}") from exc


def category_items() -> tuple[tuple[str, str, str], ...]:
    return tuple((spec.id, spec.label, spec.description) for spec in CATALOG.values())


def interface_data(category: str) -> list[dict[str, Any]]:
    """Stable dump of a category interface. Used as a golden and by docs."""
    spec = get_category(category)
    return [
        {
            "name": s.name,
            "socket": s.socket,
            "default": s.default,
            "min": s.min,
            "max": s.max,
            "subtype": s.subtype,
            "panel": s.panel,
        }
        for s in spec.sockets
    ]


def validate_catalog() -> list[str]:
    errors: list[str] = []
    if tuple(CATALOG) != CATEGORIES:
        errors.append(f"catalog keys {tuple(CATALOG)} != protocol {CATEGORIES}")
    for spec in CATALOG.values():
        names = [s.name for s in spec.sockets]
        if len(names) != len(set(names)):
            errors.append(f"{spec.id}: duplicate socket names")
        for master_socket, principled in spec.principled_map.items():
            if master_socket not in names:
                errors.append(f"{spec.id}: map key {master_socket!r} is not a socket")
            if not principled:
                errors.append(f"{spec.id}: empty Principled target for {master_socket!r}")
    return errors
