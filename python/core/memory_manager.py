"""
Module de gestion mémoire pour la synchronisation N2F.

Ce module fournit un gestionnaire de mémoire intelligent qui :
- Surveille l'utilisation mémoire des DataFrames
- Libère automatiquement la mémoire selon des stratégies LRU
- Nettoie la mémoire par scope
- Fournit des métriques d'utilisation mémoire
"""

import time
import gc
import psutil
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


@dataclass
class DataFrameInfo:
    """Informations sur un DataFrame en mémoire."""
    dataframe: pd.DataFrame
    size_mb: float
    access_time: float
    scope: str
    name: str
    creation_time: float = field(default_factory=time.time)


@dataclass
class MemoryMetrics:
    """Métriques d'utilisation mémoire."""
    current_usage_mb: float = 0.0
    peak_usage_mb: float = 0.0
    total_dataframes: int = 0
    freed_memory_mb: float = 0.0
    cleanup_count: int = 0
    last_cleanup_time: float = 0.0


class MemoryManager:
    """
    Gestionnaire de mémoire intelligent pour les DataFrames.

    Fonctionnalités :
    - Surveillance de l'utilisation mémoire
    - Libération automatique selon stratégie LRU
    - Nettoyage par scope
    - Métriques détaillées
    - Protection contre la surconsommation
    """

    def __init__(self, max_memory_mb: int = 1024, cleanup_threshold: float = 0.8):
        """
        Initialise le gestionnaire de mémoire.

        Args:
            max_memory_mb: Limite mémoire en MB (défaut: 1GB)
            cleanup_threshold: Seuil de déclenchement du nettoyage (0.8 = 80%)
        """
        self.max_memory_mb = max_memory_mb
        self.cleanup_threshold = cleanup_threshold
        self.dataframes: Dict[str, DataFrameInfo] = {}
        self.metrics = MemoryMetrics()
        self.process = psutil.Process()

        print(f"MemoryManager initialisé - Limite: {max_memory_mb}MB, Seuil: {cleanup_threshold*100}%")

    def register_dataframe(self, name: str, df: pd.DataFrame, scope: str = "default") -> bool:
        """
        Enregistre un DataFrame avec gestion de la mémoire.

        Args:
            name: Nom unique du DataFrame
            df: DataFrame à enregistrer
            scope: Scope de synchronisation (ex: "users", "projects")

        Returns:
            bool: True si l'enregistrement a réussi
        """
        # Calcul de la taille du DataFrame
        size_mb = self._calculate_dataframe_size(df)

        # Vérification de la limite mémoire
        if self.metrics.current_usage_mb + size_mb > self.max_memory_mb * self.cleanup_threshold:
            self._cleanup_oldest()

        # Si toujours trop de mémoire après nettoyage, refuser l'enregistrement
        if self.metrics.current_usage_mb + size_mb > self.max_memory_mb:
            print(f"⚠️  Impossible d'enregistrer {name} - Mémoire insuffisante "
                  f"({self.metrics.current_usage_mb:.1f}MB + {size_mb:.1f}MB > {self.max_memory_mb}MB)")
            return False

        # Enregistrement du DataFrame
        self.dataframes[name] = DataFrameInfo(
            dataframe=df,
            size_mb=size_mb,
            access_time=time.time(),
            scope=scope,
            name=name
        )

        # Mise à jour des métriques
        self.metrics.current_usage_mb += size_mb
        self.metrics.total_dataframes += 1
        self.metrics.peak_usage_mb = max(self.metrics.peak_usage_mb, self.metrics.current_usage_mb)

        print(f"📊 DataFrame '{name}' enregistré - Taille: {size_mb:.1f}MB, "
              f"Total: {self.metrics.current_usage_mb:.1f}MB/{self.max_memory_mb}MB")

        return True

    def get_dataframe(self, name: str) -> Optional[pd.DataFrame]:
        """
        Récupère un DataFrame avec mise à jour du temps d'accès.

        Args:
            name: Nom du DataFrame à récupérer

        Returns:
            DataFrame ou None si non trouvé
        """
        if name in self.dataframes:
            # Mise à jour du temps d'accès
            self.dataframes[name].access_time = time.time()
            return self.dataframes[name].dataframe
        return None

    def cleanup_scope(self, scope_name: str) -> float:
        """
        Libère la mémoire d'un scope spécifique.

        Args:
            scope_name: Nom du scope à nettoyer

        Returns:
            float: Mémoire libérée en MB
        """
        keys_to_remove = [
            k for k in self.dataframes.keys()
            if self.dataframes[k].scope == scope_name
        ]

        freed_memory = 0.0
        for key in keys_to_remove:
            freed_memory += self.dataframes[key].size_mb
            del self.dataframes[key]

        # Mise à jour des métriques
        self.metrics.current_usage_mb -= freed_memory
        self.metrics.freed_memory_mb += freed_memory
        self.metrics.cleanup_count += 1
        self.metrics.last_cleanup_time = time.time()

        if freed_memory > 0:
            print(f"🧹 Scope '{scope_name}' nettoyé - {freed_memory:.1f}MB libérés, "
                  f"Reste: {self.metrics.current_usage_mb:.1f}MB")

        return freed_memory

    def cleanup_all(self) -> float:
        """
        Libère toute la mémoire utilisée.

        Returns:
            float: Mémoire libérée en MB
        """
        freed_memory = self.metrics.current_usage_mb

        # Libération de tous les DataFrames
        self.dataframes.clear()

        # Mise à jour des métriques
        self.metrics.current_usage_mb = 0.0
        self.metrics.freed_memory_mb += freed_memory
        self.metrics.cleanup_count += 1
        self.metrics.last_cleanup_time = time.time()

        # Forcer le garbage collector
        gc.collect()

        print(f"🧹 Nettoyage complet - {freed_memory:.1f}MB libérés")
        return freed_memory

    def get_memory_stats(self) -> Dict:
        """
        Retourne les statistiques d'utilisation mémoire.

        Returns:
            Dict: Statistiques détaillées
        """
        # Mémoire système
        system_memory = psutil.virtual_memory()

        return {
            "memory_manager": {
                "current_usage_mb": self.metrics.current_usage_mb,
                "peak_usage_mb": self.metrics.peak_usage_mb,
                "max_memory_mb": self.max_memory_mb,
                "usage_percentage": (self.metrics.current_usage_mb / self.max_memory_mb) * 100,
                "total_dataframes": self.metrics.total_dataframes,
                "active_dataframes": len(self.dataframes),
                "freed_memory_mb": self.metrics.freed_memory_mb,
                "cleanup_count": self.metrics.cleanup_count
            },
            "system": {
                "total_memory_mb": system_memory.total / 1024 / 1024,
                "available_memory_mb": system_memory.available / 1024 / 1024,
                "memory_percentage": system_memory.percent,
                "process_memory_mb": self.process.memory_info().rss / 1024 / 1024
            },
            "dataframes_by_scope": self._get_dataframes_by_scope()
        }

    def print_memory_summary(self):
        """Affiche un résumé de l'utilisation mémoire."""
        stats = self.get_memory_stats()

        print("\n" + "="*60)
        print("📊 RÉSUMÉ MÉMOIRE")
        print("="*60)

        # Mémoire du gestionnaire
        mm = stats["memory_manager"]
        print(f"🔹 Utilisation actuelle: {mm['current_usage_mb']:.1f}MB / {mm['max_memory_mb']}MB ({mm['usage_percentage']:.1f}%)")
        print(f"🔹 Pic d'utilisation: {mm['peak_usage_mb']:.1f}MB")
        print(f"🔹 DataFrames actifs: {mm['active_dataframes']} / {mm['total_dataframes']} total")
        print(f"🔹 Mémoire libérée: {mm['freed_memory_mb']:.1f}MB ({mm['cleanup_count']} nettoyages)")

        # Mémoire système
        sys = stats["system"]
        print(f"🔹 Mémoire système: {sys['memory_percentage']:.1f}% utilisée")
        print(f"🔹 Processus: {sys['process_memory_mb']:.1f}MB")

        # DataFrames par scope
        print("\n📁 DataFrames par scope:")
        for scope, info in stats["dataframes_by_scope"].items():
            print(f"   • {scope}: {info['count']} DataFrames, {info['size_mb']:.1f}MB")

        print("="*60)

    def _calculate_dataframe_size(self, df: pd.DataFrame) -> float:
        """Calcule la taille d'un DataFrame en MB."""
        return df.memory_usage(deep=True).sum() / 1024 / 1024

    def _cleanup_oldest(self):
        """Libère les DataFrames les plus anciens selon la stratégie LRU."""
        if not self.dataframes:
            return

        # Tri par temps d'accès (plus ancien en premier)
        sorted_dataframes = sorted(
            self.dataframes.items(),
            key=lambda x: x[1].access_time
        )

        # Libération des plus anciens jusqu'à atteindre le seuil
        target_memory = self.max_memory_mb * self.cleanup_threshold * 0.5  # Libérer jusqu'à 50% du seuil

        freed_memory = 0.0
        for name, info in sorted_dataframes:
            if self.metrics.current_usage_mb - freed_memory <= target_memory:
                break

            freed_memory += info.size_mb
            del self.dataframes[name]

        # Mise à jour des métriques
        self.metrics.current_usage_mb -= freed_memory
        self.metrics.freed_memory_mb += freed_memory
        self.metrics.cleanup_count += 1
        self.metrics.last_cleanup_time = time.time()

        if freed_memory > 0:
            print(f"🧹 Nettoyage LRU - {freed_memory:.1f}MB libérés, "
                  f"Reste: {self.metrics.current_usage_mb:.1f}MB")

    def _get_dataframes_by_scope(self) -> Dict[str, Dict]:
        """Groupe les DataFrames par scope."""
        scope_stats = {}

        for info in self.dataframes.values():
            if info.scope not in scope_stats:
                scope_stats[info.scope] = {"count": 0, "size_mb": 0.0}

            scope_stats[info.scope]["count"] += 1
            scope_stats[info.scope]["size_mb"] += info.size_mb

        return scope_stats


# Instance globale du gestionnaire de mémoire
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(max_memory_mb: int = 1024) -> MemoryManager:
    """
    Retourne l'instance globale du gestionnaire de mémoire.

    Args:
        max_memory_mb: Limite mémoire en MB (utilisé seulement à la première création)

    Returns:
        MemoryManager: Instance du gestionnaire de mémoire
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(max_memory_mb=max_memory_mb)
    return _memory_manager


def register_dataframe(name: str, df: pd.DataFrame, scope: str = "default") -> bool:
    """Fonction utilitaire pour enregistrer un DataFrame."""
    return get_memory_manager().register_dataframe(name, df, scope)


def get_dataframe(name: str) -> Optional[pd.DataFrame]:
    """Fonction utilitaire pour récupérer un DataFrame."""
    return get_memory_manager().get_dataframe(name)


def cleanup_scope(scope_name: str) -> float:
    """Fonction utilitaire pour nettoyer un scope."""
    return get_memory_manager().cleanup_scope(scope_name)


def cleanup_all() -> float:
    """Fonction utilitaire pour nettoyer toute la mémoire."""
    return get_memory_manager().cleanup_all()


def print_memory_summary():
    """Fonction utilitaire pour afficher le résumé mémoire."""
    get_memory_manager().print_memory_summary()


def get_memory_stats() -> Dict:
    """Fonction utilitaire pour obtenir les statistiques mémoire."""
    return get_memory_manager().get_memory_stats()
