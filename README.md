# philiprehberger-cache-kit

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

### Other Operations

```python
cache.has("key")        # check existence
cache.delete("key")     # delete single entry
cache.keys()            # list all non-expired keys
cache.clear()           # remove everything
```

## License

MIT
