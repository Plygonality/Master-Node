#!/usr/bin/env python3
"""Copy the Master Node add-on into Blender's scripts/addons folder.

Usage:
  python scripts/install_addon.py
  python scripts/install_addon.py --addons-dir /path/to/scripts/addons
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path


def candidate_addon_dirs() -> list[Path]:
    home = Path.home()
    system = platform.system()
    roots: list[Path] = []
    if system == "Darwin":
        roots.append(home / "Library/Application Support/Blender")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            roots.append(Path(appdata) / "Blender Foundation" / "Blender")
    else:
        roots.append(home / ".config" / "blender")

    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for version_dir in sorted(root.iterdir(), reverse=True):
            addons = version_dir / "scripts" / "addons"
            if addons.is_dir():
                found.append(addons)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Master Node add-on")
    parser.add_argument("--addons-dir", type=Path, default=None)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    env_dir = os.environ.get("MASTER_NODE_ADDONS_DIR")
    detected = candidate_addon_dirs()

    if args.list:
        if not detected:
            print("No Blender addons folders detected.")
            return 1
        for path in detected:
            print(path)
        return 0

    src = Path(__file__).resolve().parents[1] / "master_node"
    if not (src / "__init__.py").is_file():
        print(f"Add-on source not found: {src}", file=sys.stderr)
        return 1

    target_root = Path(args.addons_dir) if args.addons_dir else (Path(env_dir) if env_dir else None)
    if target_root is None:
        if not detected:
            print(
                "Could not find a Blender addons folder. Pass --addons-dir, or install "
                "manually: Blender → Edit → Preferences → Add-ons → Install…",
                file=sys.stderr,
            )
            return 1
        target_root = detected[0]
        print(f"Using detected addons dir: {target_root}")

    dest = target_root / "master_node"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"Installed add-on → {dest}")
    print(
        "Next: Blender → Preferences → Add-ons → enable 'Material: Master Node'. "
        "3D Viewport → N → Master Node."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
