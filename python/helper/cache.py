import pandas as pd
from typing import Any, Dict, Tuple, Optional


#
# Simple in-memory cache for get_* functions to avoid redundant API calls
# The cache key is based on the function name and its effective parameters
#
_GET_CACHE: Dict[Tuple[str, Tuple[Any, ...]], pd.DataFrame] = {}


def _make_cache_key(function_name: str, *parts: Any) -> Tuple[str, Tuple[Any, ...]]:
    return function_name, tuple(parts)


# Public helpers
def make_cache_key(function_name: str, *parts: Any) -> Tuple[str, Tuple[Any, ...]]:
    return _make_cache_key(function_name, *parts)


def get_from_cache(function_name: str, *parts: Any) -> Optional[pd.DataFrame]:
    key = _make_cache_key(function_name, *parts)
    if key in _GET_CACHE:
        return _GET_CACHE[key].copy(deep=True)
    return None


def set_in_cache(result: pd.DataFrame, function_name: str, *parts: Any) -> None:
    key = _make_cache_key(function_name, *parts)
    _GET_CACHE[key] = result


def invalidate_cache_key(function_name: str, *parts: Any) -> None:
    key = _make_cache_key(function_name, *parts)
    if key in _GET_CACHE:
        del _GET_CACHE[key]


def clear_cache() -> None:
    _GET_CACHE.clear()
