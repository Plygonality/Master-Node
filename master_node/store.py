"""Load free and paid presets from disk next to the add-on."""

from __future__ import annotations

from pathlib import Path

from master_node.core.presets import (
    Preset,
    PresetListing,
    listings_for,
    load_dir,
    load_paid_catalog,
)

DATA_DIR = Path(__file__).resolve().parent / "data" / "presets"


def free_dir() -> Path:
    return DATA_DIR / "free"


def paid_catalog_path() -> Path:
    return DATA_DIR / "paid" / "catalog.json"


def load_free() -> list[Preset]:
    return load_dir(free_dir(), tier="free")


def load_paid(paid_pack_dir: str = "") -> list[Preset]:
    presets: list[Preset] = []
    bundled = DATA_DIR / "paid"
    presets.extend(load_dir(bundled, tier="paid"))
    if paid_pack_dir:
        presets.extend(load_dir(Path(paid_pack_dir), tier="paid"))
    return presets


def all_presets(paid_pack_dir: str = "") -> list[Preset]:
    return load_free() + load_paid(paid_pack_dir)


def preset_by_id(preset_id: str, paid_pack_dir: str = "") -> Preset | None:
    for preset in all_presets(paid_pack_dir):
        if preset.id == preset_id:
            return preset
    return None


def panel_listings(category: str, license_key: str, paid_pack_dir: str = "") -> list[PresetListing]:
    return listings_for(
        all_presets(paid_pack_dir),
        load_paid_catalog(paid_catalog_path()),
        category=category,
        license_key=license_key,
    )
