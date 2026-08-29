"""Preset looks are value packs against a category interface.

The framework is public. A preset is free or paid. Paid looks do not apply
without a license — the catalog can still list them so the panel can lock them.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from master_node.core.catalog import get_category
from master_node.core.license import can_apply
from master_node.core.protocol import CATEGORIES, FORMAT_VERSION, Tier, is_known_category

PRESET_FORMAT = "master-node-preset"


@dataclass(frozen=True)
class Preset:
    id: str
    name: str
    category: str
    tier: Tier
    values: dict[str, Any]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": PRESET_FORMAT,
            "version": FORMAT_VERSION,
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "tier": self.tier,
            "description": self.description,
            "values": self.values,
        }


@dataclass(frozen=True)
class PresetListing:
    """A row the panel can draw. Paid rows may have empty values until unlocked."""

    id: str
    name: str
    category: str
    tier: Tier
    description: str = ""
    locked: bool = False


class PresetError(ValueError):
    pass


def from_dict(data: dict[str, Any]) -> Preset:
    if data.get("format") not in (PRESET_FORMAT, None):
        raise PresetError(f"unknown preset format: {data.get('format')!r}")
    preset_id = str(data.get("id") or "").strip()
    name = str(data.get("name") or "").strip()
    category = str(data.get("category") or "").strip().lower()
    tier = data.get("tier", "free")
    values = data.get("values") or {}
    if not preset_id or not name:
        raise PresetError("preset needs id and name")
    if not is_known_category(category):
        raise PresetError(f"unknown category: {category}")
    if tier not in ("free", "paid"):
        raise PresetError(f"unknown tier: {tier}")
    if not isinstance(values, dict):
        raise PresetError("values must be an object")
    return Preset(
        id=preset_id,
        name=name,
        category=category,
        tier=tier,  # type: ignore[arg-type]
        values={str(k): v for k, v in values.items()},
        description=str(data.get("description") or ""),
    )


def loads(text: str) -> Preset:
    return from_dict(json.loads(text))


def dumps(preset: Preset) -> str:
    return json.dumps(preset.to_dict(), indent=2, sort_keys=False) + "\n"


def validate_preset(preset: Preset) -> list[str]:
    errors: list[str] = []
    spec = get_category(preset.category)
    sockets = spec.socket_map()
    for name, value in preset.values.items():
        if name not in sockets:
            errors.append(f"{preset.id}: unknown socket {name!r} for {preset.category}")
            continue
        socket = sockets[name]
        errors.extend(_type_errors(preset.id, name, socket.socket, value))
    return errors


def _type_errors(preset_id: str, name: str, kind: str, value: Any) -> list[str]:
    if kind == "FLOAT":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return [f"{preset_id}: {name} expects a float"]
    elif kind == "COLOR":
        if not _is_vec(value, 3, 4):
            return [f"{preset_id}: {name} expects a color [r, g, b] or [r, g, b, a]"]
    elif kind == "VECTOR":
        if not _is_vec(value, 3, 3):
            return [f"{preset_id}: {name} expects a vector [x, y, z]"]
    elif kind == "INT":
        if not isinstance(value, int) or isinstance(value, bool):
            return [f"{preset_id}: {name} expects an int"]
    elif kind == "BOOL":
        if not isinstance(value, bool):
            return [f"{preset_id}: {name} expects a bool"]
    return []


def _is_vec(value: Any, min_len: int, max_len: int) -> bool:
    if not isinstance(value, (list, tuple)):
        return False
    if not min_len <= len(value) <= max_len:
        return False
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)


def apply_values(preset: Preset, license_key: str = "") -> dict[str, Any]:
    """Return the values to write onto the bound master, or raise if locked."""
    if not can_apply(preset.tier, license_key):
        raise PermissionError(f"preset {preset.id!r} is paid")
    return dict(preset.values)


def load_dir(path: Path, *, tier: Tier | None = None) -> list[Preset]:
    presets: list[Preset] = []
    if not path.is_dir():
        return presets
    for file in sorted(path.glob("*.json")):
        if file.name.startswith("_") or file.name == "catalog.json":
            continue
        data = json.loads(file.read_text(encoding="utf-8"))
        if isinstance(data, list):
            items = data
        else:
            items = [data]
        for item in items:
            preset = from_dict(item)
            if tier is not None and preset.tier != tier:
                continue
            presets.append(preset)
    return presets


def load_paid_catalog(path: Path) -> list[PresetListing]:
    """Names-only catalog so the panel can show locked paid looks."""
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("presets", data if isinstance(data, list) else [])
    listings: list[PresetListing] = []
    for row in rows:
        category = str(row.get("category") or "").strip().lower()
        if category not in CATEGORIES:
            continue
        listings.append(
            PresetListing(
                id=str(row.get("id") or ""),
                name=str(row.get("name") or ""),
                category=category,
                tier="paid",
                description=str(row.get("description") or ""),
                locked=True,
            )
        )
    return listings


def listings_for(
    presets: Iterable[Preset],
    paid_catalog: Iterable[PresetListing],
    *,
    category: str | None = None,
    license_key: str = "",
) -> list[PresetListing]:
    rows: list[PresetListing] = []
    seen: set[str] = set()
    for preset in presets:
        if category and preset.category != category:
            continue
        locked = not can_apply(preset.tier, license_key)
        rows.append(
            PresetListing(
                id=preset.id,
                name=preset.name,
                category=preset.category,
                tier=preset.tier,
                description=preset.description,
                locked=locked,
            )
        )
        seen.add(preset.id)
    if not can_apply("paid", license_key):
        for listing in paid_catalog:
            if listing.id in seen:
                continue
            if category and listing.category != category:
                continue
            rows.append(listing)
    return rows
