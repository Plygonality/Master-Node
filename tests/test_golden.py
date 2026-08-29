from __future__ import annotations

import json
import os
from pathlib import Path

from master_node.core.catalog import CATALOG, interface_data

GOLDENS = Path(__file__).resolve().parent / "goldens"
UPDATE = os.environ.get("UPDATE_GOLDENS") == "1"


def test_category_interface_goldens() -> None:
    for category in CATALOG:
        path = GOLDENS / f"{category}.json"
        dump = interface_data(category)
        if UPDATE:
            path.write_text(json.dumps(dump, indent=2) + "\n", encoding="utf-8")
        assert path.is_file(), f"missing golden {path.name} — run UPDATE_GOLDENS=1 pytest tests/test_golden.py"
        expected = json.loads(path.read_text(encoding="utf-8"))
        assert dump == expected, f"{category} interface drifted — UPDATE_GOLDENS=1 if intentional"
