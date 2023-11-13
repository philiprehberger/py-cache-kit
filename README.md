# philiprehberger-cache-kit

[![Tests](https://github.com/philiprehberger/py-cache-kit/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-cache-kit/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-cache-kit.svg)](https://pypi.org/project/philiprehberger-cache-kit/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-cache-kit)](https://github.com/philiprehberger/py-cache-kit/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-cache-kit)](https://github.com/philiprehberger/py-cache-kit/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-cache-kit)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-cache-kit/bug)](https://github.com/philiprehberger/py-cache-kit/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-cache-kit/enhancement)](https://github.com/philiprehberger/py-cache-kit/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Lightweight in-memory cache with TTL, LRU eviction, and tag-based invalidation.

## Installation

```bash
pip install philiprehberger-cache-kit
```

## Usage

### Basic Cache

```python
from philiprehberger_cache_kit import Cache

cache: Cache[str] = Cache(max_size=1000)

cache.set("key", "value")
print(cache.get("key"))  # "value"
```

### TTL (Time-to-Live)

```python
cache = Cache(default_ttl=60.0)  # 60 seconds default

cache.set("session", "abc123")           # uses default TTL
cache.set("temp", "data", ttl=5.0)       # expires in 5 seconds
cache.set("permanent", "data", ttl=None) # no expiry when default is set
```

### LRU Eviction

```python
cache = Cache(max_size=100)

# When full, least recently used entries are evicted first
# Expired entries are evicted before non-expired ones
for i in range(200):
    cache.set(f"key-{i}", f"value-{i}")

print(cache.size)  # 100
```

### Tag-Based Invalidation

```python
cache.set("user:1", user_data, tags={"users", "team-a"})
cache.set("user:2", user_data, tags={"users", "team-b"})
cache.set("post:1", post_data, tags={"posts", "team-a"})

# Invalidate all entries tagged "team-a"
removed = cache.invalidate_by_tag("team-a")
print(removed)  # 2
```

### Batch Operations

```python
# Set multiple entries at once
cache.set_many({"a": 1, "b": 2, "c": 3}, ttl=30.0)

# Get multiple entries at once (skips missing/expired)
results = cache.get_many(["a", "b", "missing"])
print(results)  # {"a": 1, "b": 2}
```

### Cache Statistics

```python
from philiprehberger_cache_kit import Cache, CacheStats

cache: Cache[str] = Cache(max_size=100)

cache.set("x", "hello")
cache.get("x")        # hit
cache.get("missing")  # miss

stats = cache.stats()
print(stats.hits)      # 1
print(stats.misses)    # 1
print(stats.hit_rate)  # 0.5
print(stats.evictions) # 0
print(stats.expired)   # 0

cache.reset_stats()    # zero out all counters
```

### Other Operations

```python
cache.has("key")        # check existence
"key" in cache          # same as has()
cache.delete("key")     # delete single entry
cache.keys()            # list all non-expired keys
len(cache)              # count of non-expired entries
cache.get_entry("key")  # get CacheEntry with tags, expires_at
cache.clear()           # remove everything
```

## API

| Function / Class | Description |
|---|---|
| `Cache(max_size=1000, default_ttl=None)` | Create a new cache |
| `.set(key, value, ttl=None, tags=None)` | Store a value |
| `.get(key, default=None)` | Retrieve a value |
| `.get_many(keys)` | Retrieve multiple values, skip missing/expired |
| `.set_many(items, ttl=None)` | Store multiple values |
| `.has(key)` | Check if key exists and is not expired |
| `.delete(key)` | Remove a key |
| `.invalidate_by_tag(tag)` | Remove all entries with a tag |
| `.clear()` | Remove all entries |
| `.keys()` | List non-expired keys |
| `.get_entry(key)` | Get `CacheEntry` object (value, expires_at, tags) |
| `.stats()` | Get `CacheStats` (hits, misses, evictions, expired, hit_rate) |
| `.reset_stats()` | Zero out all stat counters |
| `.size` | Number of stored entries |
| `len(cache)` | Number of non-expired entries |
| `key in cache` | Check key existence |
| `CacheStats` | Dataclass with hits, misses, evictions, expired, hit_rate |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
