"""
Module de cache amélioré pour la synchronisation N2F.

Ce module fournit un système de cache avancé avec :
- Cache en mémoire et persistant
- Gestion de l'expiration des données
- Métriques de performance
- Invalidation sélective
- Configuration centralisée
"""

import json
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import pandas as pd
import hashlib


@dataclass
class CacheEntry:
    """Entrée dans le cache avec métadonnées."""

    data: Any
    timestamp: float
    ttl: Optional[int] = None  # Time to live en secondes
    access_count: int = 0
    last_access: float = 0.0
    size_bytes: int = 0


@dataclass
class CacheMetrics:
    """Métriques du cache."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    invalidations: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0


class AdvancedCache:
    """
    Système de cache avancé avec persistance et métriques.

    Fonctionnalités :
    - Cache en mémoire avec persistance sur disque
    - Gestion de l'expiration (TTL)
    - Métriques de performance
    - Invalidation sélective
    - Compression des données
    """

    def __init__(
        self, cache_dir: Path = None, max_size_mb: int = 100, default_ttl: int = 3600
    ):
        """
        Initialise le cache avancé.

        Args:
            cache_dir: Répertoire pour la persistance (None = pas de persistance)
            max_size_mb: Taille maximale du cache en MB
            default_ttl: TTL par défaut en secondes (1 heure)
        """
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl

        # Cache en mémoire
        self._memory_cache: Dict[str, CacheEntry] = {}

        # Métriques
        self.metrics = CacheMetrics()

        # Initialisation du répertoire de cache
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_persistent_cache()

    def _make_key(self, function_name: str, *args: Any) -> str:
        """Crée une clé de cache unique."""
        # Création d'une clé basée sur la fonction et ses arguments
        key_parts = [function_name] + list(args)
        key_string = json.dumps(key_parts, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_file_path(self, key: str) -> Path:
        """Retourne le chemin du fichier de cache pour une clé."""
        return self.cache_dir / f"{key}.cache"

    def _serialize_data(self, data: Any) -> bytes:
        """Sérialise les données pour la persistance."""
        if isinstance(data, pd.DataFrame):
            return pickle.dumps(data)
        else:
            return pickle.dumps(data)

    def _deserialize_data(self, data_bytes: bytes) -> Any:
        """Désérialise les données depuis la persistance."""
        return pickle.loads(data_bytes)

    def _calculate_size(self, data: Any) -> int:
        """Calcule la taille approximative des données en bytes."""
        if isinstance(data, pd.DataFrame):
            return len(data.to_csv(index=False).encode())
        elif isinstance(data, (dict, list)):
            return len(json.dumps(data).encode())
        else:
            return len(str(data).encode())

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Vérifie si une entrée de cache a expiré."""
        if entry.ttl is None:
            return False
        return time.time() - entry.timestamp > entry.ttl

    def _cleanup_expired(self) -> None:
        """Nettoie les entrées expirées."""
        current_time = time.time()
        expired_keys = []

        for key, entry in self._memory_cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_entry(key)

    def _remove_entry(self, key: str) -> None:
        """Supprime une entrée du cache."""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            self.metrics.total_size_bytes -= entry.size_bytes
            self.metrics.entry_count -= 1
            del self._memory_cache[key]

            # Suppression du fichier persistant
            if self.cache_dir:
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    cache_file.unlink()

    def _evict_if_needed(self) -> None:
        """Évince des entrées si le cache est trop plein."""
        if self.metrics.total_size_bytes <= self.max_size_bytes:
            return

        # Éviction LRU (Least Recently Used)
        entries = sorted(self._memory_cache.items(), key=lambda x: x[1].last_access)

        while self.metrics.total_size_bytes > self.max_size_bytes * 0.8 and entries:
            key, _ = entries.pop(0)
            self._remove_entry(key)

    def _save_entry(self, key: str, entry: CacheEntry) -> None:
        """Sauvegarde une entrée en persistance."""
        if not self.cache_dir:
            return

        try:
            cache_file = self._get_cache_file_path(key)
            entry_data = {
                "data": self._serialize_data(entry.data),
                "timestamp": entry.timestamp,
                "ttl": entry.ttl,
                "access_count": entry.access_count,
                "last_access": entry.last_access,
                "size_bytes": entry.size_bytes,
            }

            with cache_file.open("wb") as f:
                pickle.dump(entry_data, f)

        except Exception as e:
            print(f"Warning: Failed to save cache entry {key}: {e}")

    def _load_entry(self, key: str) -> Optional[CacheEntry]:
        """Charge une entrée depuis la persistance."""
        if not self.cache_dir:
            return None

        try:
            cache_file = self._get_cache_file_path(key)
            if not cache_file.exists():
                return None

            with cache_file.open("rb") as f:
                entry_data = pickle.load(f)

            return CacheEntry(
                data=self._deserialize_data(entry_data["data"]),
                timestamp=entry_data["timestamp"],
                ttl=entry_data["ttl"],
                access_count=entry_data["access_count"],
                last_access=entry_data["last_access"],
                size_bytes=entry_data["size_bytes"],
            )

        except Exception as e:
            print(f"Warning: Failed to load cache entry {key}: {e}")
            return None

    def _load_persistent_cache(self) -> None:
        """Charge le cache persistant au démarrage."""
        if not self.cache_dir:
            return

        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                key = cache_file.stem
                entry = self._load_entry(key)
                if entry and not self._is_expired(entry):
                    self._memory_cache[key] = entry
                    self.metrics.total_size_bytes += entry.size_bytes
                    self.metrics.entry_count += 1

        except Exception as e:
            print(f"Warning: Failed to load persistent cache: {e}")

    def get(self, function_name: str, *args: Any) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            function_name: Nom de la fonction
            *args: Arguments de la fonction

        Returns:
            Données en cache ou None si non trouvé/expiré
        """
        key = self._make_key(function_name, *args)

        # Nettoyage des entrées expirées
        self._cleanup_expired()

        # Recherche en mémoire
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if not self._is_expired(entry):
                # Mise à jour des métriques d'accès
                entry.access_count += 1
                entry.last_access = time.time()
                self.metrics.hits += 1

                # Retour d'une copie pour éviter la modification
                if isinstance(entry.data, pd.DataFrame):
                    return entry.data.copy(deep=True)
                else:
                    return entry.data

        # Recherche en persistance
        if self.cache_dir:
            entry = self._load_entry(key)
            if entry and not self._is_expired(entry):
                # Restauration en mémoire
                self._memory_cache[key] = entry
                self.metrics.total_size_bytes += entry.size_bytes
                self.metrics.entry_count += 1
                self.metrics.hits += 1

                if isinstance(entry.data, pd.DataFrame):
                    return entry.data.copy(deep=True)
                else:
                    return entry.data

        self.metrics.misses += 1
        return None

    def set(
        self, data: Any, function_name: str, *args: Any, ttl: Optional[int] = None
    ) -> None:
        """
        Stocke une valeur dans le cache.

        Args:
            data: Données à stocker
            function_name: Nom de la fonction
            *args: Arguments de la fonction
            ttl: Time to live en secondes (None = TTL par défaut)
        """
        key = self._make_key(function_name, *args)

        # Nettoyage et éviction si nécessaire
        self._cleanup_expired()
        self._evict_if_needed()

        # Création de l'entrée
        current_time = time.time()
        size_bytes = self._calculate_size(data)

        entry = CacheEntry(
            data=data,
            timestamp=current_time,
            ttl=ttl if ttl is not None else self.default_ttl,
            access_count=0,
            last_access=current_time,
            size_bytes=size_bytes,
        )

        # Suppression de l'ancienne entrée si elle existe
        if key in self._memory_cache:
            self._remove_entry(key)

        # Ajout de la nouvelle entrée
        self._memory_cache[key] = entry
        self.metrics.total_size_bytes += size_bytes
        self.metrics.entry_count += 1
        self.metrics.sets += 1

        # Sauvegarde en persistance
        self._save_entry(key, entry)

    def invalidate(self, function_name: str, *args: Any) -> bool:
        """
        Invalide une entrée du cache.

        Args:
            function_name: Nom de la fonction
            *args: Arguments de la fonction

        Returns:
            True si l'entrée était présente et a été supprimée
        """
        key = self._make_key(function_name, *args)

        if key in self._memory_cache:
            self._remove_entry(key)
            self.metrics.invalidations += 1
            return True

        # Suppression du fichier persistant même si pas en mémoire
        if self.cache_dir:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
                self.metrics.invalidations += 1
                return True

        return False

    def clear(self) -> None:
        """Vide complètement le cache."""
        self._memory_cache.clear()
        self.metrics.total_size_bytes = 0
        self.metrics.entry_count = 0

        # Suppression des fichiers persistants
        if self.cache_dir:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du cache."""
        hit_rate = 0.0
        if self.metrics.hits + self.metrics.misses > 0:
            hit_rate = self.metrics.hits / (self.metrics.hits + self.metrics.misses)

        return {
            "hits": self.metrics.hits,
            "misses": self.metrics.misses,
            "sets": self.metrics.sets,
            "invalidations": self.metrics.invalidations,
            "hit_rate": hit_rate,
            "total_size_mb": self.metrics.total_size_bytes / (1024 * 1024),
            "entry_count": self.metrics.entry_count,
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
        }

    def get_stats(self) -> str:
        """Retourne les statistiques du cache sous forme de texte."""
        metrics = self.get_metrics()
        return (
            f"Cache Stats:\n"
            f"  Hits: {metrics['hits']}\n"
            f"  Misses: {metrics['misses']}\n"
            f"  Hit Rate: {metrics['hit_rate']:.2%}\n"
            f"  Sets: {metrics['sets']}\n"
            f"  Invalidations: {metrics['invalidations']}\n"
            f"  Entries: {metrics['entry_count']}\n"
            f"  Size: {metrics['total_size_mb']:.2f} MB / {metrics['max_size_mb']:.2f} MB"
        )


# Instance globale du cache avancé
_advanced_cache: Optional[AdvancedCache] = None


def get_cache(
    cache_dir: Path = None, max_size_mb: int = 100, default_ttl: int = 3600
) -> AdvancedCache:
    """
    Récupère l'instance globale du cache avancé.

    Args:
        cache_dir: Répertoire pour la persistance
        max_size_mb: Taille maximale en MB
        default_ttl: TTL par défaut en secondes

    Returns:
        Instance du cache avancé
    """
    global _advanced_cache

    if _advanced_cache is None:
        _advanced_cache = AdvancedCache(
            cache_dir=cache_dir, max_size_mb=max_size_mb, default_ttl=default_ttl
        )

    return _advanced_cache


def cache_get(function_name: str, *args: Any) -> Optional[Any]:
    """Fonction utilitaire pour récupérer du cache."""
    cache = get_cache()
    return cache.get(function_name, *args)


def cache_set(
    data: Any, function_name: str, *args: Any, ttl: Optional[int] = None
) -> None:
    """Fonction utilitaire pour stocker en cache."""
    cache = get_cache()
    cache.set(data, function_name, *args, ttl=ttl)


def cache_invalidate(function_name: str, *args: Any) -> bool:
    """Fonction utilitaire pour invalider le cache."""
    cache = get_cache()
    return cache.invalidate(function_name, *args)


def cache_clear() -> None:
    """Fonction utilitaire pour vider le cache."""
    cache = get_cache()
    cache.clear()


def cache_stats() -> str:
    """Fonction utilitaire pour obtenir les statistiques du cache."""
    cache = get_cache()
    return cache.get_stats()
