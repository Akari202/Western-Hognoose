import json
import urllib.request
from logging import debug, error, info
from typing import Any, Dict, Optional

from disk_dict import DiskDict


_cache_instance: Optional[DiskDict] = None
_cache_filename: str = "./cache/json_cache.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (akari202@akada.dev)"
}
DEFAULT_TIMEOUT = 10


def set_cache_file(filename: str) -> None:
    global _cache_instance, _cache_filename
    _cache_filename = filename
    _cache_instance = DiskDict(filename=filename)


def set_cache_instance(instance: DiskDict) -> None:
    global _cache_instance
    _cache_instance = instance


def _get_cache() -> DiskDict:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DiskDict(filename=_cache_filename)
    return _cache_instance


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
) -> Dict[str, Any]:
    url = upgrade_to_https(url)
    req_headers = DEFAULT_HEADERS.copy()
    if headers:
        req_headers.update(headers)

    cache = _get_cache()

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
) -> Dict[str, Any]:
    return get(url, headers=headers, timeout=timeout, use_cache=False)


def pop_cached_json(
    url: str, default: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    url = upgrade_to_https(url)
    cache = _get_cache()

    cached_data = cache.pop(url, None)
    if cached_data is None:
        return default

    return cached_data
