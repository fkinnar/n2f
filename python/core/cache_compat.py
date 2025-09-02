"""
Couche de compatibilité pour l'ancien cache simple.
Ce module fournit les mêmes fonctions que helper.cache mais utilise le cache avancé de core.
"""

from typing import Any, Optional
import pandas as pd
from .cache import cache_get, cache_set, cache_invalidate, cache_clear


def make_cache_key(function_name: str, *parts: Any) -> str:
    """Crée une clé de cache pour une fonction et ses paramètres."""
    # Convertir les paramètres en string pour la clé
    key_parts = [function_name] + [str(part) for part in parts]
    return "|".join(key_parts)


def get_from_cache(function_name: str, *parts: Any) -> Optional[pd.DataFrame]:
    """Récupère un résultat du cache."""
    key = make_cache_key(function_name, *parts)
    return cache_get(key)


def set_in_cache(result: pd.DataFrame, function_name: str, *parts: Any) -> None:
    """Stocke un résultat dans le cache."""
    key = make_cache_key(function_name, *parts)
    cache_set(result, key)


def invalidate_cache_key(function_name: str, *parts: Any) -> None:
    """Invalide une entrée spécifique du cache."""
    key = make_cache_key(function_name, *parts)
    cache_invalidate(key)


def clear_cache() -> None:
    """Vide complètement le cache."""
    cache_clear()
