"""Resolve which category master a material is bound to.

No bpy. The addon adapter walks Blender data into ``NodeRec`` / ``MasterRec``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from master_node.core.protocol import Binding, MasterRec, NodeRec


def resolve_binding(
    material: str,
    marked_group: str | None,
    nodes: Sequence[NodeRec],
    masters: Mapping[str, MasterRec],
) -> Binding | None:
    """Pick the bound master for one material.

    Order:
    1. Material marker ``mn.master`` if that group is a master *and* instanced
       in the tree (or exists as a master even if the instance name drifted).
    2. First ``ShaderNodeGroup`` in the tree whose group is a marked master.
    """
    if marked_group:
        master = masters.get(marked_group)
        if master is not None:
            node_name = _first_instance(nodes, marked_group)
            return Binding(
                material=material,
                group=master.name,
                category=master.category,
                node=node_name,
                origin=master.origin,
                version=master.version,
                source="marker",
            )

    for node in nodes:
        if node.bl_idname != "ShaderNodeGroup" or not node.group:
            continue
        master = masters.get(node.group)
        if master is None:
            continue
        return Binding(
            material=material,
            group=master.name,
            category=master.category,
            node=node.name,
            origin=master.origin,
            version=master.version,
            source="walk",
        )
    return None


def _first_instance(nodes: Sequence[NodeRec], group: str) -> str | None:
    for node in nodes:
        if node.group == group:
            return node.name
    return None
