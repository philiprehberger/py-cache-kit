from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable, TypeVar, Generic

T = TypeVar("T")

_MISSING: object = object()


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float | None
    tags: set[str]


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


class Cache(Generic[T]):
    def __init__(self, max_size: int = 1000, default_ttl: float | None = None) -> None:
        self._max_size = max_size
        self._default_ttl = default_ttl
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        self._store: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._stats = CacheStats()

    @property
    def size(self) -> int:
        self._cleanup_expired()
        return len(self._store)

    def set(
        self,
        key: str,
        value: T,
        ttl: float | None = None,
        tags: set[str] | None = None,
    ) -> None:
        effective_ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.monotonic() + effective_ttl if effective_ttl is not None else None

        if key in self._store:
            self._store.move_to_end(key)
            self._store[key] = CacheEntry(value=value, expires_at=expires_at, tags=tags or set())
        else:
            self._cleanup_expired()
            if len(self._store) >= self._max_size:
                self._evict()
            self._store[key] = CacheEntry(value=value, expires_at=expires_at, tags=tags or set())

    def get(self, key: str, default: T | None = None) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            self._stats.misses += 1
            return default

        if entry.expires_at is not None and time.monotonic() > entry.expires_at:
            del self._store[key]
            self._stats.expired += 1
            self._stats.misses += 1
            return default

        self._stats.hits += 1
        self._store.move_to_end(key)
        return entry.value

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        *,
        ttl: float | None = None,
        tags: list[str] | None = None,
    ) -> T:
        """Return the cached value, or compute and cache it if missing/expired.

        First checks ``get(key)`` using a private sentinel as the default.
          - On hit (counts as a hit), returns the cached value (which may be ``None``).
          - On miss (counts as a miss), invokes ``compute_fn()`` exactly once,
            calls ``set(key, value, ttl=ttl, tags=tags)``, and returns the value.

        Stats: exactly one ``get()`` call is performed, so each invocation is
        counted as either a hit or a miss — never both.
        """
        cached = self.get(key, default=_MISSING)  # type: ignore[arg-type]
        if cached is not _MISSING:
            return cached  # type: ignore[return-value]
        value = compute_fn()
        tag_set: set[str] | None = set(tags) if tags is not None else None
        self.set(key, value, ttl=ttl, tags=tag_set)
        return value

    def get_many(self, keys: list[str]) -> dict[str, T]:
        result: dict[str, T] = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, items: dict[str, T], ttl: float | None = None) -> None:
        for key, value in items.items():
            self.set(key, value, ttl=ttl)

    def stats(self) -> CacheStats:
        return CacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            expired=self._stats.expired,
        )

    def reset_stats(self) -> None:
        self._stats = CacheStats()

    def has(self, key: str) -> bool:
        entry = self._store.get(key)
        if entry is None:
            return False
        if entry.expires_at is not None and time.monotonic() > entry.expires_at:
            del self._store[key]
            return False
        return True

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def invalidate_by_tag(self, tag: str) -> int:
        keys_to_delete = [k for k, v in self._store.items() if tag in v.tags]
        for key in keys_to_delete:
            del self._store[key]
        return len(keys_to_delete)

    def invalidate_by_tags(self, tags: Iterable[str]) -> int:
        """Remove every entry tagged with any of *tags* in a single pass.

        Equivalent to calling :meth:`invalidate_by_tag` for each tag, but
        traverses the store only once and only counts each entry once even
        if it matches multiple tags.

        Args:
            tags: Iterable of tag strings.

        Returns:
            The number of entries that were removed.
        """
        tag_set = set(tags)
        if not tag_set:
            return 0
        keys_to_delete = [
            k for k, v in self._store.items() if v.tags & tag_set
        ]
        for key in keys_to_delete:
            del self._store[key]
        return len(keys_to_delete)

    def clear(self) -> None:
        self._store.clear()

    def keys(self) -> list[str]:
        self._cleanup_expired()
        return list(self._store.keys())

    def __len__(self) -> int:
        self._cleanup_expired()
        return len(self._store)

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def get_entry(self, key: str) -> CacheEntry[T] | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at is not None and time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        return entry

    def _evict(self) -> None:
        self._cleanup_expired()
        if len(self._store) >= self._max_size and self._store:
            self._store.popitem(last=False)
            self._stats.evictions += 1

    def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, v in self._store.items() if v.expires_at is not None and now > v.expires_at]
        for key in expired:
            del self._store[key]
            self._stats.expired += 1
