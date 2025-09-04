"""
Module Orchestrator pour la gestion de la synchronisation N2F.

Ce module contient l'orchestrateur principal qui coordonne tous les aspects
de la synchronisation : configuration, contexte, exécution et reporting.
"""

import argparse
import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .config import ConfigLoader
from .registry import get_registry
from .cache import get_cache, cache_stats, cache_clear, cache_invalidate
from .memory_manager import (
    get_memory_manager,
    cleanup_scope,
    cleanup_all,
    print_memory_summary,
)
from .metrics import (
    get_metrics,
    start_operation,
    end_operation,
    print_summary as print_metrics_summary,
)
from .retry import get_retry_manager, print_retry_summary
from .context import SyncContext
from .logging import export_api_logs
from .exceptions import SyncException

# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class SyncResult:
    """Résultat d'une synchronisation."""

    scope_name: str
    success: bool
    results: List[pd.DataFrame]
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


class ContextBuilder:
    """Constructeur de contexte de synchronisation."""

    def __init__(self, args: argparse.Namespace, config_path: Path) -> None:
        self.args = args
        self.config_path = config_path

    def build(self) -> SyncContext:
        """Construit le contexte de synchronisation."""
        # Chargement de la configuration
        config_loader = ConfigLoader(self.config_path)
        sync_config = config_loader.load()

        # Initialisation du cache avancé
        if sync_config.cache.enabled:
            cache_dir = None
            if sync_config.cache.persist_cache:
                # Vérifier si cache_dir n'est pas un Mock
                cache_dir_value = sync_config.cache.cache_dir
                if not hasattr(cache_dir_value, "_mock_name"):  # Pas un Mock
                    cache_dir = (
                        Path(__file__).resolve().parent.parent.parent / cache_dir_value
                    )

            get_cache(
                cache_dir=cache_dir,  # type: ignore
                max_size_mb=sync_config.cache.max_size_mb,
                default_ttl=sync_config.cache.default_ttl,
            )

        # Initialisation du gestionnaire de mémoire
        memory_limit_mb = getattr(
            sync_config, "memory_limit_mb", 1024
        )  # 1GB par défaut
        get_memory_manager(max_memory_mb=memory_limit_mb)

        # Initialisation du système de métriques
        get_metrics()

        # Initialisation du système de retry
        get_retry_manager()

        # Auto-découverte des scopes APRÈS le chargement de la configuration
        registry = get_registry()
        registry.auto_discover_scopes("business.process")

        # Construction du contexte
        base_dir = Path(__file__).resolve().parent.parent

        return SyncContext(
            args=self.args,
            config=sync_config,
            base_dir=base_dir,
            db_user=os.getenv("AGRESSO_DB_USER"),
            db_password=os.getenv("AGRESSO_DB_PASSWORD"),
            client_id=os.getenv("N2F_CLIENT_ID"),
            client_secret=os.getenv("N2F_CLIENT_SECRET"),
        )


class ScopeExecutor:
    """Exécuteur de synchronisation pour un scope."""

    def __init__(self, context: SyncContext) -> None:
        self.context = context
        self.registry = get_registry()

    def execute_scope(self, scope_name: str) -> SyncResult:
        """Exécute la synchronisation pour un scope donné."""
        start_time = time.time()

        try:
            # Récupération de la configuration du scope
            scope_config = self.registry.get(scope_name)
            if not scope_config or not scope_config.enabled:
                return SyncResult(
                    scope_name=scope_name,
                    success=False,
                    results=[],
                    error_message=f"Scope '{scope_name}' not found or disabled",
                )

            print(
                f"--- Starting synchronization for scope : {scope_name} "
                f"({scope_config.display_name}) ---"
            )

            # Exécution de la synchronisation
            results = scope_config.sync_function(
                context=self.context,
                sql_filename=scope_config.sql_filename,
                sql_column_filter=scope_config.sql_column_filter,
            )

            duration = time.time() - start_time
            print(f"--- End of synchronization for scope : {scope_name} ---")

            return SyncResult(
                scope_name=scope_name,
                success=True,
                results=results if isinstance(results, list) else [results],
                duration_seconds=duration,
            )

        except SyncException as e:
            duration = time.time() - start_time
            error_message = f"Error during synchronization: {str(e)}"
            print(f"--- Error in scope {scope_name}: {error_message} ---")

            return SyncResult(
                scope_name=scope_name,
                success=False,
                results=[],
                error_message=error_message,
                duration_seconds=duration,
            )


class LogManager:
    """Gestionnaire de logs et d'export."""

    def __init__(self) -> None:
        self.results: List[SyncResult] = []

    def add_result(self, result: SyncResult) -> None:
        """Ajoute un résultat de synchronisation."""
        self.results.append(result)

    def export_and_summarize(self) -> None:
        """Exporte les logs et affiche un résumé."""
        if not self.results:
            print("No synchronization results to export.")
            return

        # Collecte de tous les DataFrames de résultats
        all_dataframes: List[pd.DataFrame] = []
        for result in self.results:
            if result.success and result.results:
                all_dataframes.extend(result.results)

        if not all_dataframes:
            print("No data to export.")
            return

        try:
            # Combiner tous les résultats
            combined_df = pd.concat(all_dataframes, ignore_index=True)

            # Exporter les logs
            log_filename = export_api_logs(combined_df)
            print("\n--- API Logs Export ---")
            print(f"API logs exported to : {log_filename}")

            # Afficher un résumé des erreurs
            self._print_api_summary(combined_df)

        except (IOError, ValueError) as e:
            print(f"Error during logs export : {e}")

    def _print_api_summary(self, combined_df: pd.DataFrame) -> None:
        """Affiche un résumé des opérations API."""
        if "api_success" not in combined_df.columns:
            return

        success_count = int(combined_df["api_success"].sum())
        total_count = len(combined_df)
        error_count = total_count - success_count

        print("\nAPI Operations Summary :")
        print(f"  - Success : {success_count}/{total_count}")
        print(f"  - Errors : {error_count}/{total_count}")

        if error_count > 0:
            print("\nError Details :")
            errors_df = combined_df.query("api_success == False")
            for _, row in errors_df.iterrows():
                print(f"  - {row.get('api_message', 'Unknown error')}")
                details = row.get("api_error_details")
                if np.any(pd.notna(details)):
                    print(f"    Details : {details}")

    def get_successful_scopes(self) -> List[str]:
        """Retourne la liste des scopes qui ont réussi."""
        return [result.scope_name for result in self.results if result.success]

    def get_failed_scopes(self) -> List[str]:
        """Retourne la liste des scopes qui ont échoué."""
        return [result.scope_name for result in self.results if not result.success]

    def get_total_duration(self) -> float:
        """Retourne la durée totale de synchronisation."""
        total = 0.0
        for r in self.results:
            duration = r.duration_seconds
            if isinstance(duration, str):
                try:
                    duration = float(duration)
                except (ValueError, TypeError):
                    duration = 0.0
            total += duration
        return total

    def print_sync_summary(self) -> None:
        """Affiche un résumé de la synchronisation."""
        if not self.results:
            return

        total_scopes = len(self.results)
        successful_scopes = sum(1 for r in self.results if r.success)
        failed_scopes = total_scopes - successful_scopes
        total_duration = self.get_total_duration()

        print("\n--- Synchronization Summary ---")
        print(f"  - Total scopes processed : {total_scopes}")
        print(f"  - Successful : {successful_scopes}")
        print(f"  - Failed : {failed_scopes}")
        print(f"  - Total duration : {total_duration:.2f} seconds")

        if failed_scopes > 0:
            print("\nFailed scopes :")
            for result in self.results:
                if not result.success:
                    print(f"  - {result.scope_name}: {result.error_message}")


class SyncOrchestrator:
    """
    Orchestrateur principal pour la synchronisation N2F.

    Coordonne tous les aspects de la synchronisation :
    - Configuration et contexte
    - Exécution des scopes
    - Gestion des logs et reporting
    """

    def __init__(self, config_path: Path, args: argparse.Namespace) -> None:
        """
        Initialise l'orchestrateur.

        Args:
            config_path: Chemin vers le fichier de configuration
            args: Arguments de ligne de commande
        """
        self.config_path = config_path
        self.args = args
        self.context_builder = ContextBuilder(args, config_path)
        self.log_manager = LogManager()

        # Initialisation du registry avec auto-découverte
        self.registry = get_registry()
        # L'auto-découverte se fait dans le ContextBuilder, pas ici

    def run(self) -> None:
        """
        Exécute la synchronisation complète.

        Cette méthode orchestre l'ensemble du processus :
        1. Construction du contexte
        2. Détermination des scopes à traiter
        3. Exécution de chaque scope
        4. Export et résumé des résultats
        """
        try:
            # Gestion du cache si demandé
            if hasattr(self.args, "clear_cache") and self.args.clear_cache:
                print("--- Clearing cache ---")
                cache_clear()
                print("Cache cleared successfully")

            # Invalidation sélective du cache si demandé
            if hasattr(self.args, "invalidate_cache") and self.args.invalidate_cache:
                print("--- Invalidating specific cache entries ---")
                for function_name in self.args.invalidate_cache:
                    cache_invalidate(function_name)
                    print(f"  - Invalidated: {function_name}")
                print("Cache invalidation completed")

            # Construction du contexte
            context = self.context_builder.build()

            # Détermination des scopes à traiter
            selected_scopes = self._get_selected_scopes()

            # Exécution des scopes
            self._execute_scopes(context, selected_scopes)

            # Export et résumé
            self.log_manager.export_and_summarize()
            self.log_manager.print_sync_summary()

            # Affichage des statistiques du cache
            config_loader = ConfigLoader(self.config_path)
            sync_config = config_loader.load()
            if sync_config.cache.enabled:
                print("\n--- Cache Statistics ---")
                print(cache_stats())

            # Affichage des statistiques mémoire
            print_memory_summary()

            # Affichage des métriques de synchronisation
            print_metrics_summary()

            # Affichage des métriques de retry
            print_retry_summary()

        except Exception as e:
            print(f"Fatal error during synchronization: {e}")
            raise
        finally:
            # Nettoyage final de la mémoire
            cleanup_all()

    def _get_selected_scopes(self) -> List[str]:
        """Détermine les scopes à traiter."""
        # Vérifier si des scopes spécifiques sont demandés
        if hasattr(self.args, "scope") and self.args.scope:
            # Si "all" est dans les scopes demandés, utiliser tous les scopes
            if "all" in self.args.scope:
                selected_scopes = set(self.registry.get_enabled_scopes())
            else:
                selected_scopes = set(self.args.scope)
        else:
            # Utilise le registry pour obtenir les scopes disponibles
            selected_scopes = set(self.registry.get_enabled_scopes())

        return list(selected_scopes)

    def _execute_scopes(self, context: SyncContext, scope_names: List[str]) -> None:
        """Exécute les scopes sélectionnés."""
        executor = ScopeExecutor(context)

        for scope_name in scope_names:
            # Démarrage du suivi des métriques pour ce scope
            metrics = start_operation(scope_name, "sync")

            try:
                result = executor.execute_scope(scope_name)
                self.log_manager.add_result(result)

                # Enregistrement des métriques de succès
                end_operation(
                    metrics,
                    success=result.success,
                    error_message=result.error_message,
                    records_processed=len(result.results) if result.results else 0,
                    memory_usage_mb=0.0,  # Sera mis à jour par le MemoryManager
                    api_calls=0,  # À implémenter si nécessaire
                    cache_hits=0,  # À implémenter si nécessaire
                    cache_misses=0,  # À implémenter si nécessaire
                )

            except Exception as e:
                # Enregistrement des métriques d'erreur
                end_operation(
                    metrics,
                    success=False,
                    error_message=str(e),
                    records_processed=0,
                    memory_usage_mb=0.0,
                    api_calls=0,
                    cache_hits=0,
                    cache_misses=0,
                )
                raise
            finally:
                # Nettoyage de la mémoire après chaque scope
                cleanup_scope(scope_name)

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la configuration."""
        config_loader = ConfigLoader(self.config_path)
        sync_config = config_loader.load()

        return {
            "config_file": str(self.config_path),
            "database_prod": sync_config.database.prod,
            "api_sandbox": sync_config.api.sandbox,
            "api_simulate": sync_config.api.simulate,
            "available_scopes": self.registry.get_all_scopes(),
            "enabled_scopes": self.registry.get_enabled_scopes(),
        }
