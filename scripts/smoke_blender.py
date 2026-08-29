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
    dump = bind_category("metal")
    assert dump["category"] == "metal"
    assert dump["group"] == "MN Metal"
    after = set_param("Roughness", 0.12)
    assert abs(after["values"]["Roughness"] - 0.12) < 1e-5
    bpy.ops.master_node.set_param(name="Anisotropy", value="0.4")
    final = get_binding()
    assert final is not None
    assert abs(final["values"]["Anisotropy"] - 0.4) < 1e-5
    print(json.dumps(final, indent=2))
    unregister()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
