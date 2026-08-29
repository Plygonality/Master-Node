from __future__ import annotations

from master_node.core.protocol import MasterRec, NodeRec
from master_node.core.resolve import resolve_binding

MASTERS = {
    "MN Metal": MasterRec("MN Metal", "metal"),
    "MN Glass": MasterRec("MN Glass", "glass", origin="user"),
}


def test_marker_wins_over_walk_order() -> None:
    nodes = [
        NodeRec("Group", group="MN Glass"),
        NodeRec("Group.001", group="MN Metal"),
    ]
    binding = resolve_binding("Steel", "MN Metal", nodes, MASTERS)
    assert binding is not None
    assert binding.group == "MN Metal"
    assert binding.category == "metal"
    assert binding.source == "marker"
    assert binding.node == "Group.001"


def test_walk_picks_first_master_instance() -> None:
    nodes = [
        NodeRec("Noise", bl_idname="ShaderNodeTexNoise"),
        NodeRec("Group", group="MN Glass"),
        NodeRec("Group.001", group="MN Metal"),
    ]
    binding = resolve_binding("Pane", None, nodes, MASTERS)
    assert binding is not None
    assert binding.group == "MN Glass"
    assert binding.source == "walk"
    assert binding.origin == "user"


def test_marker_without_instance_still_binds() -> None:
    binding = resolve_binding("Orphan", "MN Metal", [], MASTERS)
    assert binding is not None
    assert binding.node is None
    assert binding.category == "metal"


def test_unknown_marker_falls_through_to_walk() -> None:
    nodes = [NodeRec("Group", group="MN Glass")]
    binding = resolve_binding("Pane", "DoesNotExist", nodes, MASTERS)
    assert binding is not None
    assert binding.group == "MN Glass"


def test_no_master() -> None:
    nodes = [NodeRec("Principled", bl_idname="ShaderNodeBsdfPrincipled")]
    assert resolve_binding("Raw", None, nodes, MASTERS) is None
