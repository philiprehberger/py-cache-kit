# Changelog

## 0.3.1 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility

## 0.3.0 (2026-03-27)

- Add `get_many()` for batch retrieval of multiple keys
- Add `set_many()` for batch insertion of multiple entries
- Add `CacheStats` dataclass with hits, misses, evictions, expired, and hit_rate
- Add `stats()` to retrieve current cache statistics
- Add `reset_stats()` to zero out stat counters
- Track hits and misses in `get()`, evictions in LRU eviction, expired in cleanup
- Add 8 badges, Support section, and issue templates to README
- Add `[tool.pytest.ini_options]` and `[tool.mypy]` to pyproject.toml

## 0.2.3

- Add Development section to README
- Add wheel build target to pyproject.toml

## 0.2.1

- Fix cache eviction to clean all expired entries before LRU fallback
- Fix `size` property to exclude expired entries

## 0.2.0

- Add `max_size` validation (must be at least 1)
- Add `__len__()` for `len(cache)` support
- Add `__contains__()` for `key in cache` support
- Add `get_entry()` to inspect cache entries
- Add comprehensive test suite (~25 tests)
- Add API reference table to README

## 0.1.2

- Update project URLs in pyproject.toml

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0
- Initial release
