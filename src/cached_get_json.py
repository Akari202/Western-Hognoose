import json
import urllib.request
from logging import debug, error, info
from typing import Any, Dict, Optional

from disk_dict import DiskDict


_cache_instances: Dict[str, DiskDict] = {}
_cache_filenames: Dict[str, str] = {"default": "./cache/json_cache.json"}

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (akari202@akada.dev)"
}
DEFAULT_TIMEOUT: int = 10


def set_cache_file(filename: str, cache_type: str = "default") -> None:
    global _cache_filenames, _cache_instances
    _cache_filenames[cache_type] = filename
    _cache_instances[cache_type] = DiskDict(filename=filename)


def set_cache_instance(instance: DiskDict, cache_type: str = "default") -> None:
    global _cache_instances
    _cache_instances[cache_type] = instance


def _get_cache(cache_type: str = "default") -> DiskDict:
    global _cache_instances
    if cache_type not in _cache_instances:
        filename = _cache_filenames.get(
            cache_type, f"./cache/{cache_type}_json_cache.json"
        )
        _cache_instances[cache_type] = DiskDict(filename=filename)
    return _cache_instances[cache_type]


def upgrade_to_https(url: str) -> str:
    if url.startswith("http://"):
        return "https://" + url[7:]
    return url


def _network_fetch(url: str, headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8").strip()
            return json.loads(raw_body)
    except Exception as e:
        error(f"Network request or JSON parsing failed for {url}: {e}")
        raise e


def get_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    use_cache: bool = True,
    cache_type: str = "default",
) -> Dict[str, Any]:
    url = upgrade_to_https(url)
    req_headers = DEFAULT_HEADERS.copy()
    if headers:
        req_headers.update(headers)

    cache = _get_cache(cache_type)

    if not use_cache:
        info(f"Cache disabled, fetching fresh json from {url}")
        json_data = _network_fetch(url, req_headers, timeout)
        cache[url] = json_data
        return json_data

    debug(f"Getting json for {url}")
    json_data = cache.get(url)

    if json_data is None:
        info(f"Cache miss, fetching fresh json from {url}")
        json_data = _network_fetch(url, req_headers, timeout)
        cache[url] = json_data
    else:
        debug(f"Using cached json")

    return json_data


def force_fetch_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    cache_type: str = "default",
) -> Dict[str, Any]:
    return get_json(
        url, headers=headers, timeout=timeout, use_cache=False, cache_type=cache_type
    )


def pop_cached_json(
    url: str,
    default: Optional[Dict[str, Any]] = None,
    cache_type: str = "default",
) -> Optional[Dict[str, Any]]:
    url = upgrade_to_https(url)
    cache = _get_cache(cache_type)

    cached_data = cache.pop(url, None)
    if cached_data is None:
        return default

    return cached_data


def clear_cache(cache_type: str = "default") -> None:
    cache = _get_cache(cache_type)
    cache.clear()
    info(f"Cleared all entries from the {cache_type} cache")
