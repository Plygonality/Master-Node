from __future__ import annotations

import pytest
from master_node.core.protocol import (
    FORMAT,
    PROP_CATEGORY,
    PROP_IS_MASTER,
    master_props,
    read_master_props,
    tree_name_for,
)


def test_tree_names() -> None:
    assert tree_name_for("metal") == "MN Metal"
    assert tree_name_for("dielectric") == "MN Dielectric"


def test_master_props_roundtrip() -> None:
    props = master_props("glass", origin="user", version=2)
    assert props[PROP_IS_MASTER] is True
    assert props[PROP_CATEGORY] == "glass"
    read = read_master_props(props)
    assert read is not None
    assert read[PROP_CATEGORY] == "glass"
    assert read["mn.origin"] == "user"
    assert read["mn.version"] == 2


def test_unknown_category_rejected() -> None:
    with pytest.raises(ValueError):
        master_props("wood")


def test_unmarked_is_not_a_master() -> None:
    assert read_master_props({"mn.category": "metal"}) is None
    assert read_master_props({PROP_IS_MASTER: True}) is None


def test_binding_dump_format() -> None:
    from master_node.core.protocol import Binding

    data = Binding("Steel", "MN Metal", "metal", node="Group").to_dict()
    assert data["format"] == FORMAT
    assert data["category"] == "metal"
    assert data["source"] == "marker"
