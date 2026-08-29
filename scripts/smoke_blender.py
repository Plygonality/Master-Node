"""Headless smoke: register the add-on, bind metal, tweak a slider.

    blender --background --python scripts/smoke_blender.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    import bpy
    from master_node import register, unregister
    from master_node.live import bind_category, get_binding, set_param

    register()
    bpy.ops.mesh.primitive_cube_add()
    from master_node.bind import binding_for, binding_node
    from master_node.core.catalog import CATALOG
    from master_node.rna_draw import apply_socket_map
    from master_node.store import load_free

    for category in CATALOG:
        dump = bind_category(category)
        assert dump["category"] == category, dump
        assert dump["group"].startswith("MN "), dump
        assert "Roughness" in dump["values"] or "Base Roughness" in dump["values"] or "Strength" in dump["values"]

    dump = bind_category("metal")
    assert dump["category"] == "metal"
    assert dump["group"] == "MN Metal"
    assert abs(dump["values"]["Rotation"] - 0.0) < 1e-4
    assert abs(dump["values"]["Coat Roughness"] - 0.03) < 1e-4
    r, g, _b, _a = dump["values"]["Color"]
    assert abs(r - 0.72) < 0.02 and abs(g - 0.72) < 0.02
    after = set_param("Roughness", 0.12)
    assert abs(after["values"]["Roughness"] - 0.12) < 1e-5
    bpy.ops.master_node.set_param(name="Anisotropy", value="0.4")
    final = get_binding()
    assert final is not None
    assert abs(final["values"]["Anisotropy"] - 0.4) < 1e-5
    assert len(final["values"]["Color"]) == 4

    chrome = next(p for p in load_free() if p.id == "metal.chrome")
    mat = bpy.context.object.active_material
    node = binding_node(mat, binding_for(mat))
    skipped = apply_socket_map(node, chrome.values, category="metal")
    assert skipped == []
    chrome_dump = get_binding()
    assert abs(chrome_dump["values"]["Roughness"] - 0.02) < 1e-5

    print(json.dumps(chrome_dump, indent=2))
    unregister()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
