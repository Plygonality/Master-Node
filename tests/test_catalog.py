from __future__ import annotations

from master_node.core.catalog import CATALOG, interface_data, validate_catalog
from master_node.core.protocol import CATEGORIES


def test_catalog_matches_protocol() -> None:
    assert tuple(CATALOG) == CATEGORIES
    assert validate_catalog() == []


def test_every_category_has_sockets() -> None:
    for spec in CATALOG.values():
        assert spec.sockets
        assert spec.tree_name.startswith("MN ")
        assert spec.principled_map


def test_interface_dump_is_stable() -> None:
    metal = interface_data("metal")
    names = [row["name"] for row in metal]
    assert names[:4] == ["Color", "Roughness", "Anisotropy", "Rotation"]
    assert metal[1]["subtype"] == "FACTOR"
    assert metal[1]["min"] == 0.0
    assert metal[1]["max"] == 1.0
