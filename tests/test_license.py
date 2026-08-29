from __future__ import annotations

from master_node.core.license import DEV_UNLOCK, can_apply, is_unlocked, normalize_key


def test_dev_key_unlocks() -> None:
    assert is_unlocked(DEV_UNLOCK)
    assert is_unlocked(f"  {DEV_UNLOCK}  ")
    assert not is_unlocked("")
    assert not is_unlocked("store-key")


def test_free_never_needs_a_key() -> None:
    assert can_apply("free", "")
    assert can_apply("paid", DEV_UNLOCK)
    assert not can_apply("paid", "")


def test_normalize() -> None:
    assert normalize_key(None) == ""
    assert normalize_key("  x  ") == "x"
