from __future__ import annotations

from pathlib import Path

import pytest
from master_node.core.license import DEV_UNLOCK
from master_node.core.presets import (
    apply_values,
    from_dict,
    listings_for,
    load_dir,
    load_paid_catalog,
    validate_preset,
)
from master_node.store import DATA_DIR, load_free, paid_catalog_path, panel_listings

FREE = Path(__file__).resolve().parents[1] / "master_node" / "data" / "presets" / "free"


def test_free_presets_validate() -> None:
    presets = load_dir(FREE, tier="free")
    assert len(presets) >= 12
    errors: list[str] = []
    for preset in presets:
        assert preset.tier == "free"
        errors.extend(validate_preset(preset))
    assert errors == [], errors


def test_store_load_free_matches_disk() -> None:
    assert DATA_DIR.name == "presets"
    assert {p.id for p in load_free()} == {p.id for p in load_dir(FREE, tier="free")}


def test_paid_apply_is_gated() -> None:
    preset = from_dict(
        {
            "id": "metal.aged_brass",
            "name": "Aged Brass",
            "category": "metal",
            "tier": "paid",
            "values": {"Roughness": 0.4},
        }
    )
    with pytest.raises(PermissionError):
        apply_values(preset, "")
    assert apply_values(preset, DEV_UNLOCK)["Roughness"] == 0.4


def test_unknown_socket_is_invalid() -> None:
    preset = from_dict(
        {
            "id": "metal.bad",
            "name": "Bad",
            "category": "metal",
            "tier": "free",
            "values": {"Not A Socket": 1.0},
        }
    )
    assert validate_preset(preset)


def test_listings_lock_paid_names() -> None:
    rows = panel_listings("metal", license_key="")
    names = {row.name: row for row in rows}
    assert "Chrome" in names
    assert names["Chrome"].locked is False
    assert "Aged Brass" in names
    assert names["Aged Brass"].locked is True
    unlocked = panel_listings("metal", license_key=DEV_UNLOCK)
    assert all(not row.locked for row in unlocked if row.tier == "free")
    assert "Aged Brass" not in {row.name for row in unlocked}


def test_paid_catalog_has_only_known_categories() -> None:
    listings = load_paid_catalog(paid_catalog_path())
    assert listings
    assert all(row.tier == "paid" and row.locked for row in listings)
    chrome_free = load_free()
    listed = listings_for(chrome_free, listings, category="glass", license_key="")
    assert any(row.id == "glass.smoked" and row.locked for row in listed)
