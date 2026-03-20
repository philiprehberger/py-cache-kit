# Changelog
## 0.2.4- Add pytest and mypy tool configuration to pyproject.toml

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
