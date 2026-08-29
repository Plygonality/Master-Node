"""Paid-preset gate.

The framework (protocol, category masters, N-panel) is public. Preset packs
are the paid layer. A key unlocks them. ``MN-DEV-UNLOCK`` is for tests and
the Plygon-mcp loop — it is not a store license.
"""

from __future__ import annotations

from master_node.core.protocol import Tier

DEV_UNLOCK = "MN-DEV-UNLOCK"


def normalize_key(key: str | None) -> str:
    return (key or "").strip()


def is_unlocked(key: str | None) -> bool:
    return normalize_key(key) == DEV_UNLOCK


def can_apply(tier: Tier | str, key: str | None) -> bool:
    if tier == "free":
        return True
    return is_unlocked(key)
