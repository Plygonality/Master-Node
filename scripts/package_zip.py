#!/usr/bin/env python3
"""Zip master_node/ for Blender → Preferences → Add-ons → Install."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "master_node"
SKIP = {"__pycache__"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "dist" / "master_node.zip")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in SRC.rglob("*"):
            if any(part in SKIP or part.endswith(".pyc") for part in path.parts):
                continue
            if path.is_file():
                zf.write(path, Path("master_node") / path.relative_to(SRC))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
