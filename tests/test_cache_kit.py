from __future__ import annotations

from unittest.mock import patch
import time

import pytest

from philiprehberger_cache_kit import Cache, CacheEntry


# --- Basics ---

def test_set_get():
    c = Cache()
    c.set("a", 1)
    assert c.get("a") == 1

def test_get_missing_returns_default():
    c = Cache()
    assert c.get("missing") is None
    assert c.get("missing", 42) == 42

def test_has_and_delete():
    c = Cache()
    c.set("a", 1)
    assert c.has("a")
    assert c.delete("a")
    assert not c.has("a")
    assert not c.delete("a")


# --- TTL ---

_time_val = [0.0]

def _mock_monotonic():
    return _time_val[0]

def test_ttl_expiry():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache()
        c.set("a", 1, ttl=5.0)
        assert c.get("a") == 1
        _time_val[0] = 6.0
        assert c.get("a") is None

def test_expired_returns_default():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache()
        c.set("a", 1, ttl=1.0)
        _time_val[0] = 2.0
        assert c.get("a", "default") == "default"

def test_default_ttl():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache(default_ttl=3.0)
        c.set("a", 1)
        _time_val[0] = 4.0
        assert c.get("a") is None


# --- Override TTL ---

def test_per_key_ttl_overrides_default():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache(default_ttl=2.0)
        c.set("a", 1, ttl=10.0)
        _time_val[0] = 5.0
        assert c.get("a") == 1


# --- LRU eviction ---

def test_lru_eviction():
    c = Cache(max_size=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.set("d", 4)  # should evict "a"
    assert c.get("a") is None
    assert c.get("d") == 4

def test_recently_accessed_survives():
    c = Cache(max_size=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.get("a")  # access "a" to make it recently used
    c.set("d", 4)  # should evict "b" (LRU)
    assert c.get("a") == 1
    assert c.get("b") is None


# --- Expired entry eviction priority ---

def test_expired_evicted_before_lru():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache(max_size=3)
        c.set("a", 1, ttl=1.0)
        c.set("b", 2)
        c.set("c", 3)
        _time_val[0] = 2.0  # "a" is now expired
        c.set("d", 4)  # should evict expired "a" instead of LRU "b"
        assert c.get("b") == 2
        assert c.get("d") == 4


# --- Tags ---

def test_set_with_tags():
    c = Cache()
    c.set("a", 1, tags={"x"})
    c.set("b", 2, tags={"x", "y"})
    removed = c.invalidate_by_tag("x")
    assert removed == 2

def test_tag_invalidation_selectivity():
    c = Cache()
    c.set("a", 1, tags={"x"})
    c.set("b", 2, tags={"y"})
    removed = c.invalidate_by_tag("x")
    assert removed == 1
    assert c.get("b") == 2
    assert c.get("a") is None


# --- clear ---

def test_clear():
    c = Cache()
    c.set("a", 1)
    c.set("b", 2)
    c.clear()
    assert c.size == 0


# --- keys ---

def test_keys():
    c = Cache()
    c.set("a", 1)
    c.set("b", 2)
    assert sorted(c.keys()) == ["a", "b"]

def test_keys_excludes_expired():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache()
        c.set("a", 1, ttl=1.0)
        c.set("b", 2)
        _time_val[0] = 2.0
        assert c.keys() == ["b"]


# --- size ---

def test_size():
    c = Cache()
    c.set("a", 1)
    c.set("b", 2)
    assert c.size == 2


# --- __len__ ---

def test_len():
    c = Cache()
    c.set("a", 1)
    c.set("b", 2)
    assert len(c) == 2


# --- __contains__ ---

def test_contains():
    c = Cache()
    c.set("a", 1)
    assert "a" in c
    assert "b" not in c

def test_contains_expired():
    with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
        _time_val[0] = 0.0
        c = Cache()
        c.set("a", 1, ttl=1.0)
        _time_val[0] = 2.0
        assert "a" not in c


# --- get_entry ---

def test_get_entry():
    c = Cache()
    c.set("a", 1, tags={"x"})
    entry = c.get_entry("a")
    assert entry is not None
    assert entry.value == 1
    assert "x" in entry.tags

def test_get_entry_missing():
    c = Cache()
    assert c.get_entry("missing") is None


# --- Overwrite ---

def test_overwrite_updates_value():
    c = Cache()
    c.set("a", 1)
    c.set("a", 2)
    assert c.get("a") == 2


# --- Validation ---

def test_max_size_zero_raises():
    with pytest.raises(ValueError, match="max_size"):
        Cache(max_size=0)


# --- size excludes expired entries ---

def test_size_excludes_expired():
    c = Cache()
    c.set("a", 1, ttl=0.01)
    c.set("b", 2, ttl=0.01)
    c.set("c", 3)
    time.sleep(0.05)
    assert c.size == 1


# --- Full cleanup on eviction ---

def test_full_cleanup_on_eviction():
    c = Cache(max_size=5)
    c.set("a", 1, ttl=0.01)
    c.set("b", 2, ttl=0.01)
    c.set("c", 3, ttl=0.01)
    c.set("d", 4)
    c.set("e", 5)
    time.sleep(0.05)
    c.set("f", 6)  # should clean all 3 expired, no LRU eviction needed
    assert c.get("d") == 4
    assert c.get("e") == 5
    assert c.get("f") == 6
    assert c.size == 3


# --- Expired cleanup before LRU ---

def test_expired_cleaned_before_lru_eviction():
    c = Cache(max_size=3)
    c.set("a", 1, ttl=0.01)
    c.set("b", 2)
    c.set("c", 3)
    time.sleep(0.05)
    c.set("d", 4)  # expired "a" cleaned, "b" (LRU) should survive
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3
    assert c.get("d") == 4


# --- get_or_compute ---

class TestGetOrCompute:
    def test_first_call_computes_and_caches(self):
        c: Cache[int] = Cache()
        calls = {"n": 0}

        def compute() -> int:
            calls["n"] += 1
            return 42

        result = c.get_or_compute("k", compute)
        assert result == 42
        assert calls["n"] == 1
        assert c.get("k") == 42

    def test_second_call_returns_cached_without_invoking_fn(self):
        c: Cache[int] = Cache()
        calls = {"n": 0}

        def compute() -> int:
            calls["n"] += 1
            return 42

        first = c.get_or_compute("k", compute)
        second = c.get_or_compute("k", compute)
        assert first == 42
        assert second == 42
        assert calls["n"] == 1  # only invoked once

    def test_ttl_honored_recomputes_after_expiry(self):
        with patch("philiprehberger_cache_kit.cache.time.monotonic", side_effect=_mock_monotonic):
            _time_val[0] = 0.0
            c: Cache[int] = Cache()
            calls = {"n": 0}

            def compute() -> int:
                calls["n"] += 1
                return calls["n"]

            assert c.get_or_compute("k", compute, ttl=5.0) == 1
            _time_val[0] = 6.0  # past expiry
            assert c.get_or_compute("k", compute, ttl=5.0) == 2
            assert calls["n"] == 2

    def test_tags_honored_invalidate_by_tag_recomputes(self):
        c: Cache[int] = Cache()
        calls = {"n": 0}

        def compute() -> int:
            calls["n"] += 1
            return calls["n"]

        assert c.get_or_compute("k", compute, tags=["users"]) == 1
        assert c.get_or_compute("k", compute, tags=["users"]) == 1  # cached
        removed = c.invalidate_by_tag("users")
        assert removed == 1
        assert c.get_or_compute("k", compute, tags=["users"]) == 2
        assert calls["n"] == 2

    def test_hit_miss_counters_update(self):
        c: Cache[int] = Cache()

        def compute() -> int:
            return 7

        c.get_or_compute("k", compute)  # miss + cache
        c.get_or_compute("k", compute)  # hit
        stats = c.stats()
        assert stats.misses >= 1
        assert stats.hits >= 1

    def test_compute_fn_returning_none_does_not_recompute(self):
        c: Cache[int | None] = Cache()
        calls = {"n": 0}

        def compute() -> None:
            calls["n"] += 1
            return None

        first = c.get_or_compute("k", compute)
        second = c.get_or_compute("k", compute)
        assert first is None
        assert second is None
        assert calls["n"] == 1  # legitimate cached None must not trigger recompute
