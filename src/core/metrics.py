"""
Module de métriques pour la synchronisation N2F.

Ce module fournit un système de métriques complet qui :
- Surveille les performances de chaque opération
- Collecte des statistiques par scope et par action
- Fournit des métriques d'utilisation mémoire
- Génère des rapports détaillés de performance
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import defaultdict
import json
from pathlib import Path


@dataclass
class OperationMetrics:
    """Métriques d'une opération spécifique."""

    scope: str
    action: str  # create, update, delete, sync
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    records_processed: int = 0
    memory_usage_mb: float = 0.0
    api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def duration_seconds(self) -> float:
        """Calcule la durée de l'opération en secondes."""
        return (self.end_time or time.time()) - self.start_time

    @property
    def records_per_second(self) -> float:
        """Calcule le nombre d'enregistrements traités par seconde."""
        duration = self.duration_seconds
        return self.records_processed / duration if duration > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les métriques en dictionnaire."""
        return {
            "scope": self.scope,
            "action": self.action,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "records_processed": self.records_processed,
            "records_per_second": self.records_per_second,
            "memory_usage_mb": self.memory_usage_mb,
            "api_calls": self.api_calls,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }


@dataclass
class ScopeMetrics:
    """Métriques consolidées pour un scope."""

    scope: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration_seconds: float = 0.0
    total_records_processed: int = 0
    peak_memory_usage_mb: float = 0.0
    total_api_calls: int = 0
    total_cache_hits: int = 0
    total_cache_misses: int = 0
    operations_by_action: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès."""
        return (
            self.successful_operations / self.total_operations
            if self.total_operations > 0
            else 0
        )

    @property
    def average_duration_seconds(self) -> float:
        """Calcule la durée moyenne des opérations."""
        return (
            self.total_duration_seconds / self.total_operations
            if self.total_operations > 0
            else 0
        )

    @property
    def cache_hit_rate(self) -> float:
        """Calcule le taux de hit du cache."""
        total_cache_operations = self.total_cache_hits + self.total_cache_misses
        return (
            self.total_cache_hits / total_cache_operations
            if total_cache_operations > 0
            else 0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les métriques en dictionnaire."""
        return {
            "scope": self.scope,
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.success_rate,
            "total_duration_seconds": self.total_duration_seconds,
            "average_duration_seconds": self.average_duration_seconds,
            "total_records_processed": self.total_records_processed,
            "peak_memory_usage_mb": self.peak_memory_usage_mb,
            "total_api_calls": self.total_api_calls,
            "cache_hit_rate": self.cache_hit_rate,
            "total_cache_hits": self.total_cache_hits,
            "total_cache_misses": self.total_cache_misses,
            "operations_by_action": self.operations_by_action,
        }


class SyncMetrics:
    """
    Système de métriques pour la synchronisation N2F.

    Collecte et analyse les métriques de performance pour :
    - Chaque opération individuelle
    - Chaque scope de synchronisation
    - L'ensemble du processus de synchronisation
    """

    def __init__(self):
        """Initialise le système de métriques."""
        self.start_time = time.time()
        self.operations: List[OperationMetrics] = []
        self.memory_usage_history: List[Dict[str, Any]] = []
        self.error_history: List[Dict[str, Any]] = []
        self.api_call_history: List[Dict[str, Any]] = []

    def start_operation(self, scope: str, action: str) -> OperationMetrics:
        """
        Démarre le suivi d'une opération.

        Args:
            scope: Nom du scope (ex: "users", "projects")
            action: Type d'action (ex: "create", "update", "delete", "sync")

        Returns:
            OperationMetrics: Objet de métriques pour l'opération
        """
        metrics = OperationMetrics(scope=scope, action=action, start_time=time.time())
        self.operations.append(metrics)
        return metrics

    def end_operation(
        self,
        metrics: OperationMetrics,
        success: bool = True,
        error_message: Optional[str] = None,
        records_processed: int = 0,
        memory_usage_mb: float = 0.0,
        api_calls: int = 0,
        cache_hits: int = 0,
        cache_misses: int = 0,
    ):
        """
        Termine le suivi d'une opération.

        Args:
            metrics: Objet de métriques retourné par start_operation
            success: True si l'opération a réussi
            error_message: Message d'erreur si échec
            records_processed: Nombre d'enregistrements traités
            memory_usage_mb: Utilisation mémoire en MB
            api_calls: Nombre d'appels API effectués
            cache_hits: Nombre de hits du cache
            cache_misses: Nombre de misses du cache
        """
        metrics.end_time = time.time()
        metrics.success = success
        metrics.error_message = error_message
        metrics.records_processed = records_processed
        metrics.memory_usage_mb = memory_usage_mb
        metrics.api_calls = api_calls
        metrics.cache_hits = cache_hits
        metrics.cache_misses = cache_misses

        # Enregistrement de l'erreur si échec
        if not success and error_message:
            self.error_history.append(
                {
                    "timestamp": time.time(),
                    "scope": metrics.scope,
                    "action": metrics.action,
                    "error_message": error_message,
                    "duration_seconds": metrics.duration_seconds,
                }
            )

        # Enregistrement de l'appel API
        if api_calls > 0:
            self.api_call_history.append(
                {
                    "timestamp": time.time(),
                    "scope": metrics.scope,
                    "action": metrics.action,
                    "api_calls": api_calls,
                    "duration_seconds": metrics.duration_seconds,
                }
            )

    def record_memory_usage(self, usage_mb: float, scope: str = "global"):
        """
        Enregistre l'utilisation mémoire.

        Args:
            usage_mb: Utilisation mémoire en MB
            scope: Scope associé à cette utilisation mémoire
        """
        self.memory_usage_history.append(
            {"timestamp": time.time(), "usage_mb": usage_mb, "scope": scope}
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé complet des métriques.

        Returns:
            Dict: Résumé détaillé des métriques
        """
        total_operations = len(self.operations)
        successful_operations = sum(1 for op in self.operations if op.success)
        failed_operations = total_operations - successful_operations

        # Calcul des durées
        total_duration = time.time() - self.start_time
        operation_durations = [op.duration_seconds for op in self.operations]
        avg_duration = (
            sum(operation_durations) / len(operation_durations)
            if operation_durations
            else 0
        )
        max_duration = max(operation_durations) if operation_durations else 0
        min_duration = min(operation_durations) if operation_durations else 0

        # Calcul des enregistrements
        total_records = sum(op.records_processed for op in self.operations)
        avg_records_per_second = (
            total_records / total_duration if total_duration > 0 else 0
        )

        # Calcul des appels API
        total_api_calls = sum(op.api_calls for op in self.operations)
        total_cache_hits = sum(op.cache_hits for op in self.operations)
        total_cache_misses = sum(op.cache_misses for op in self.operations)
        cache_hit_rate = (
            total_cache_hits / (total_cache_hits + total_cache_misses)
            if (total_cache_hits + total_cache_misses) > 0
            else 0
        )

        # Calcul de la mémoire
        memory_usages = [entry["usage_mb"] for entry in self.memory_usage_history]
        peak_memory = max(memory_usages) if memory_usages else 0
        avg_memory = sum(memory_usages) / len(memory_usages) if memory_usages else 0

        return {
            "summary": {
                "total_duration_seconds": total_duration,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": (
                    successful_operations / total_operations
                    if total_operations > 0
                    else 0
                ),
                "total_records_processed": total_records,
                "average_records_per_second": avg_records_per_second,
            },
            "performance": {
                "average_duration_seconds": avg_duration,
                "max_duration_seconds": max_duration,
                "min_duration_seconds": min_duration,
                "total_api_calls": total_api_calls,
                "cache_hit_rate": cache_hit_rate,
                "total_cache_hits": total_cache_hits,
                "total_cache_misses": total_cache_misses,
            },
            "memory": {
                "peak_usage_mb": peak_memory,
                "average_usage_mb": avg_memory,
                "memory_samples": len(self.memory_usage_history),
            },
            "operations_by_scope": self._group_operations_by_scope(),
            "operations_by_action": self._group_operations_by_action(),
            "error_summary": self._group_errors(),
            "api_call_summary": self._group_api_calls(),
        }

    def get_scope_metrics(self, scope: str) -> Optional[ScopeMetrics]:
        """
        Retourne les métriques consolidées pour un scope spécifique.

        Args:
            scope: Nom du scope

        Returns:
            ScopeMetrics ou None si le scope n'existe pas
        """
        scope_operations = [op for op in self.operations if op.scope == scope]
        if not scope_operations:
            return None

        metrics = ScopeMetrics(scope=scope)

        for op in scope_operations:
            metrics.total_operations += 1
            if op.success:
                metrics.successful_operations += 1
            else:
                metrics.failed_operations += 1

            metrics.total_duration_seconds += op.duration_seconds
            metrics.total_records_processed += op.records_processed
            metrics.peak_memory_usage_mb = max(
                metrics.peak_memory_usage_mb, op.memory_usage_mb
            )
            metrics.total_api_calls += op.api_calls
            metrics.total_cache_hits += op.cache_hits
            metrics.total_cache_misses += op.cache_misses

            # Comptage par action
            action = op.action
            metrics.operations_by_action[action] = (
                metrics.operations_by_action.get(action, 0) + 1
            )

        return metrics

    def export_metrics(self, output_path: Optional[Path] = None) -> Path:
        """
        Exporte les métriques au format JSON.

        Args:
            output_path: Chemin de sortie (optionnel)

        Returns:
            Path: Chemin du fichier exporté
        """
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"metrics_{timestamp}.json")

        # Préparation des données d'export
        export_data = {
            "metadata": {
                "export_timestamp": time.time(),
                "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_operations": len(self.operations),
            },
            "summary": self.get_summary(),
            "operations": [op.to_dict() for op in self.operations],
            "memory_history": self.memory_usage_history,
            "error_history": self.error_history,
            "api_call_history": self.api_call_history,
        }

        # Export au format JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return output_path

    def print_summary(self):
        """Affiche un résumé des métriques dans la console."""
        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("RÉSUMÉ DES MÉTRIQUES DE SYNCHRONISATION")
        print("=" * 70)

        # Résumé général
        print(
            f"Durée totale: {summary['summary']['total_duration_seconds']:.2f} secondes"
        )
        print(
            f"Opérations: {summary['summary']['successful_operations']}/{summary['summary']['total_operations']} réussies ({summary['summary']['success_rate']*100:.1f}%)"
        )
        print(
            f"Enregistrements traités: {summary['summary']['total_records_processed']:,}"
        )
        print(
            f"Performance: {summary['summary']['average_records_per_second']:.1f} enregistrements/seconde"
        )

        # Performance
        print(f"\nPERFORMANCE:")
        print(
            f"   - Durée moyenne: {summary['performance']['average_duration_seconds']:.2f}s"
        )
        print(f"   - Durée max: {summary['performance']['max_duration_seconds']:.2f}s")
        print(f"   - Appels API: {summary['performance']['total_api_calls']}")
        print(
            f"   - Cache hit rate: {summary['performance']['cache_hit_rate']*100:.1f}%"
        )

        # Mémoire
        print(f"\nMÉMOIRE:")
        print(f"   - Pic d'utilisation: {summary['memory']['peak_usage_mb']:.1f}MB")
        print(
            f"   - Utilisation moyenne: {summary['memory']['average_usage_mb']:.1f}MB"
        )

        # Par scope
        print(f"\nPAR SCOPE:")
        for scope, scope_data in summary["operations_by_scope"].items():
            success_rate = (
                scope_data["success"] / scope_data["total"] * 100
                if scope_data["total"] > 0
                else 0
            )
            print(
                f"   - {scope}: {scope_data['success']}/{scope_data['total']} ({success_rate:.1f}%)"
            )

        # Erreurs
        if summary["error_summary"]:
            print(f"\nERREURS:")
            for error, count in summary["error_summary"].items():
                print(f"   - {error}: {count} occurrence(s)")

        print("=" * 70)

    def _group_operations_by_scope(self) -> Dict[str, Dict[str, int]]:
        """Groupe les opérations par scope."""
        result = defaultdict(lambda: {"total": 0, "success": 0, "errors": 0})
        for op in self.operations:
            result[op.scope]["total"] += 1
            if op.success:
                result[op.scope]["success"] += 1
            else:
                result[op.scope]["errors"] += 1
        return dict(result)

    def _group_operations_by_action(self) -> Dict[str, Dict[str, Any]]:
        """Groupe les opérations par action."""
        result = defaultdict(
            lambda: {
                "count": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "total_records": 0,
                "total_api_calls": 0,
            }
        )

        for op in self.operations:
            result[op.action]["count"] += 1
            result[op.action]["total_duration"] += op.duration_seconds
            result[op.action]["total_records"] += op.records_processed
            result[op.action]["total_api_calls"] += op.api_calls
            if op.success:
                result[op.action]["success_count"] += 1

        # Calcul des moyennes
        for action_data in result.values():
            if action_data["count"] > 0:
                action_data["average_duration"] = (
                    action_data["total_duration"] / action_data["count"]
                )
                action_data["success_rate"] = (
                    action_data["success_count"] / action_data["count"]
                )

        return dict(result)

    def _group_errors(self) -> Dict[str, int]:
        """Groupe les erreurs par type."""
        errors = defaultdict(int)
        for op in self.operations:
            if not op.success and op.error_message:
                errors[op.error_message] += 1
        return dict(errors)

    def _group_api_calls(self) -> Dict[str, Any]:
        """Groupe les appels API par scope."""
        result = defaultdict(lambda: {"total_calls": 0, "total_duration": 0.0})
        for op in self.operations:
            if op.api_calls > 0:
                result[op.scope]["total_calls"] += op.api_calls
                result[op.scope]["total_duration"] += op.duration_seconds

        # Calcul des moyennes
        for scope_data in result.values():
            if scope_data["total_calls"] > 0:
                scope_data["average_duration_per_call"] = (
                    scope_data["total_duration"] / scope_data["total_calls"]
                )

        return dict(result)


# Instance globale du système de métriques
_metrics: Optional[SyncMetrics] = None


def get_metrics() -> SyncMetrics:
    """
    Retourne l'instance globale du système de métriques.

    Returns:
        SyncMetrics: Instance du système de métriques
    """
    global _metrics
    if _metrics is None:
        _metrics = SyncMetrics()
    return _metrics


def start_operation(scope: str, action: str) -> OperationMetrics:
    """Fonction utilitaire pour démarrer une opération."""
    return get_metrics().start_operation(scope, action)


def end_operation(metrics: OperationMetrics, **kwargs):
    """Fonction utilitaire pour terminer une opération."""
    get_metrics().end_operation(metrics, **kwargs)


def record_memory_usage(usage_mb: float, scope: str = "global"):
    """Fonction utilitaire pour enregistrer l'utilisation mémoire."""
    get_metrics().record_memory_usage(usage_mb, scope)


def get_summary() -> Dict[str, Any]:
    """Fonction utilitaire pour obtenir le résumé des métriques."""
    return get_metrics().get_summary()


def print_summary():
    """Fonction utilitaire pour afficher le résumé des métriques."""
    get_metrics().print_summary()


def export_metrics(output_path: Optional[Path] = None) -> Path:
    """Fonction utilitaire pour exporter les métriques."""
    return get_metrics().export_metrics(output_path)


def reset_metrics():
    """Réinitialise les métriques globales."""
    global _metrics
    _metrics = SyncMetrics()
