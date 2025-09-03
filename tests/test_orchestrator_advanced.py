#!/usr/bin/env python3
"""
Tests avancés pour le module src/core/orchestrator.py.

Ce module teste les fonctionnalités avancées de l'orchestrateur.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Ajouter le répertoire python au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

# Imports après modification du path
from core.orchestrator import SyncOrchestrator, LogManager, SyncResult
from core.config import SyncConfig, DatabaseConfig, ApiConfig, CacheConfig
from core.registry import SyncRegistry
from core import SyncContext


class TestLogManagerAdvanced(unittest.TestCase):
    """Tests avancés pour LogManager."""

    def setUp(self):
        """Configuration initiale."""
        self.log_manager = LogManager()

        # Créer des résultats de test
        self.success_result = SyncResult(
            scope_name="test_scope",
            success=True,
            duration_seconds=1.5,
            error_message="",
            results=[
                pd.DataFrame(
                    {
                        "api_success": [True, True, False],
                        "api_message": ["Success", "Success", "Error"],
                        "api_error_details": [None, None, "Test error"],
                    }
                )
            ],
        )

        self.failed_result = SyncResult(
            scope_name="failed_scope",
            success=False,
            duration_seconds=0.5,
            error_message="Test error",
            results=[],
        )

    def test_export_api_logs_with_data(self):
        """Test d'export des logs API avec des données."""
        # Ajouter des résultats
        self.log_manager.add_result(self.success_result)
        self.log_manager.add_result(self.failed_result)

        # Tester l'export
        with patch("core.orchestrator.export_api_logs") as mock_export:
            mock_export.return_value = "test_logs.csv"

            self.log_manager.export_and_summarize()

            # Vérifier que export_api_logs a été appelé
            mock_export.assert_called_once()

            # Vérifier que le DataFrame passé contient les bonnes données
            call_args = mock_export.call_args[0][0]
            self.assertIsInstance(call_args, pd.DataFrame)
            self.assertEqual(len(call_args), 3)  # 3 lignes de données

    def test_export_api_logs_no_data(self):
        """Test d'export des logs API sans données."""
        # Pas de résultats ajoutés

        with patch("builtins.print") as mock_print:
            self.log_manager.export_and_summarize()

            # Vérifier que le message "No synchronization results to export" est affiché
            mock_print.assert_called_with("No synchronization results to export.")

    def test_export_api_logs_exception(self):
        """Test d'export des logs API avec exception."""
        self.log_manager.add_result(self.success_result)

        with patch("core.orchestrator.export_api_logs") as mock_export:
            mock_export.side_effect = Exception("Export error")

            with patch("builtins.print") as mock_print:
                self.log_manager.export_and_summarize()

                # Vérifier que l'erreur est affichée
                mock_print.assert_called_with("Error during logs export : Export error")

    def test_print_api_summary_with_errors(self):
        """Test d'affichage du résumé API avec des erreurs."""
        self.log_manager.add_result(self.success_result)

        with patch("builtins.print") as mock_print:
            self.log_manager._print_api_summary(self.success_result.results[0])

            # Vérifier que le résumé est affiché
            calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertIn("\nAPI Operations Summary :", calls)
            self.assertIn("\nError Details :", calls)

    def test_print_api_summary_no_success_column(self):
        """Test d'affichage du résumé API sans colonne api_success."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})

        with patch("builtins.print") as mock_print:
            self.log_manager._print_api_summary(df)

            # Vérifier qu'aucun résumé n'est affiché
            mock_print.assert_not_called()

    def test_get_successful_scopes(self):
        """Test de récupération des scopes réussis."""
        self.log_manager.add_result(self.success_result)
        self.log_manager.add_result(self.failed_result)

        successful_scopes = self.log_manager.get_successful_scopes()

        self.assertEqual(successful_scopes, ["test_scope"])

    def test_get_failed_scopes(self):
        """Test de récupération des scopes échoués."""
        self.log_manager.add_result(self.success_result)
        self.log_manager.add_result(self.failed_result)

        failed_scopes = self.log_manager.get_failed_scopes()

        self.assertEqual(failed_scopes, ["failed_scope"])

    def test_get_total_duration_with_string_duration(self):
        """Test de calcul de la durée totale avec durée en string."""
        result_with_string = SyncResult(
            scope_name="string_duration_scope",
            success=True,
            duration_seconds="2.5",  # String au lieu de float
            error_message="",
            results=[],
        )

        self.log_manager.add_result(result_with_string)

        total_duration = self.log_manager.get_total_duration()

        self.assertEqual(total_duration, 2.5)

    def test_get_total_duration_with_invalid_string(self):
        """Test de calcul de la durée totale avec string invalide."""
        result_with_invalid_string = SyncResult(
            scope_name="invalid_duration_scope",
            success=True,
            duration_seconds="invalid",  # String invalide
            error_message="",
            results=[],
        )

        self.log_manager.add_result(result_with_invalid_string)

        total_duration = self.log_manager.get_total_duration()

        self.assertEqual(total_duration, 0.0)

    def test_print_sync_summary_with_failures(self):
        """Test d'affichage du résumé de synchronisation avec échecs."""
        self.log_manager.add_result(self.success_result)
        self.log_manager.add_result(self.failed_result)

        with patch("builtins.print") as mock_print:
            self.log_manager.print_sync_summary()

            # Vérifier que le résumé est affiché
            calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertIn("\n--- Synchronization Summary ---", calls)
            self.assertIn("\nFailed scopes :", calls)

    def test_print_sync_summary_no_results(self):
        """Test d'affichage du résumé de synchronisation sans résultats."""
        with patch("builtins.print") as mock_print:
            self.log_manager.print_sync_summary()

            # Vérifier qu'aucun résumé n'est affiché
            mock_print.assert_not_called()


class TestSyncOrchestratorAdvanced(unittest.TestCase):
    """Tests avancés pour SyncOrchestrator."""

    def setUp(self):
        """Configuration initiale."""
        # Créer une configuration de test
        self.config = SyncConfig(
            database=DatabaseConfig(prod=False),
            api=ApiConfig(
                base_urls="https://test.api.com", sandbox=True, simulate=False
            ),
            scopes={},
            cache=CacheConfig(enabled=True, default_ttl=3600, max_size_mb=100),
        )

        # Créer un fichier de configuration temporaire
        self.temp_config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        self.temp_config_file.write(
            """
database:
  host: test_host
  port: 1433
  database: test_db
  username: test_user
  password: test_pass
  prod: false
api:
  base_url: https://test.api.com
  client_id: test_client
  client_secret: test_secret
  sandbox: true
  simulate: false
scopes: {}
cache:
  enabled: true
  ttl: 3600
  max_size: 100
        """
        )
        self.temp_config_file.close()

        # Créer l'orchestrator
        self.orchestrator = SyncOrchestrator(Path(self.temp_config_file.name), Mock())

    def tearDown(self):
        """Nettoyage."""
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)

    @patch("core.orchestrator.ConfigLoader")
    @patch("core.registry.SyncRegistry")
    @patch("core.orchestrator.SyncContext")
    @patch("core.orchestrator.ScopeExecutor")
    @patch("core.orchestrator.start_operation")
    @patch("core.orchestrator.end_operation")
    @patch("core.orchestrator.cleanup_scope")
    @patch("core.orchestrator.cleanup_all")
    @patch("core.orchestrator.cache_stats")
    @patch("core.orchestrator.print_memory_summary")
    @patch("core.orchestrator.print_metrics_summary")
    @patch("core.orchestrator.print_retry_summary")
    def test_run_with_specific_scopes(
        self,
        mock_retry_summary,
        mock_metrics_summary,
        mock_memory_summary,
        mock_cache_stats,
        mock_cleanup_all,
        mock_cleanup_scope,
        mock_end_operation,
        mock_start_operation,
        mock_executor,
        mock_context,
        mock_registry,
        mock_config_loader,
    ):
        """Test d'exécution avec des scopes spécifiques."""
        # Configuration des mocks
        mock_config_loader.return_value.load.return_value = self.config
        mock_registry.return_value.get_enabled_scopes.return_value = ["users", "axes"]
        mock_context.return_value = Mock()
        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        # Simuler un résultat de succès
        success_result = SyncResult(
            scope_name="users",
            success=True,
            duration_seconds=1.0,
            error_message="",
            results=[],
        )
        mock_executor_instance.execute_scope.return_value = success_result

        # Configurer les arguments pour des scopes spécifiques
        self.orchestrator.args = Mock()
        self.orchestrator.args.scopes = ["users"]
        self.orchestrator.args.invalidate_cache = None  # Pas d'invalidation de cache

        # Exécuter
        self.orchestrator.run()

        # Vérifications
        mock_start_operation.assert_called_once()
        mock_end_operation.assert_called_once()
        mock_cleanup_scope.assert_called_once_with("users")
        mock_cleanup_all.assert_called_once()

    @patch("core.orchestrator.ConfigLoader")
    @patch("core.registry.SyncRegistry")
    @patch("core.orchestrator.SyncContext")
    @patch("core.orchestrator.ScopeExecutor")
    @patch("core.orchestrator.start_operation")
    @patch("core.orchestrator.end_operation")
    @patch("core.orchestrator.cleanup_scope")
    @patch("core.orchestrator.cleanup_all")
    @patch("core.orchestrator.print_memory_summary")
    def test_run_with_scope_execution_error(
        self,
        mock_print_memory_summary,
        mock_cleanup_all,
        mock_cleanup_scope,
        mock_end_operation,
        mock_start_operation,
        mock_executor,
        mock_context,
        mock_registry,
        mock_config_loader,
    ):
        """Test d'exécution avec erreur lors de l'exécution d'un scope."""
        # Configuration des mocks
        mock_config_loader.return_value.load.return_value = self.config
        mock_registry.return_value.get_enabled_scopes.return_value = ["users"]
        mock_context.return_value = Mock()
        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        # Simuler une exception lors de l'exécution
        mock_executor_instance.execute_scope.side_effect = Exception(
            "Scope execution error"
        )

        # Configurer les arguments
        self.orchestrator.args = Mock()
        self.orchestrator.args.scopes = ["users"]
        self.orchestrator.args.invalidate_cache = None  # Pas d'invalidation de cache

        # Exécuter et vérifier que l'exception est levée
        with self.assertRaises(Exception):
            self.orchestrator.run()

        # Vérifier que end_operation a été appelé avec success=False
        mock_end_operation.assert_called_once()
        call_args = mock_end_operation.call_args[1]
        self.assertFalse(call_args["success"])
        self.assertEqual(call_args["error_message"], "Scope execution error")

    def test_get_selected_scopes_with_specific_scopes(self):
        """Test de sélection des scopes avec des scopes spécifiques."""
        self.orchestrator.args = Mock()
        self.orchestrator.args.scopes = ["users", "axes"]

        selected_scopes = self.orchestrator._get_selected_scopes()

        # L'ordre n'est pas important, vérifier seulement que les deux scopes sont
        # présents
        self.assertEqual(set(selected_scopes), {"users", "axes"})

    @patch("core.orchestrator.get_registry")
    def test_get_selected_scopes_from_registry(self, mock_get_registry):
        """Test de sélection des scopes depuis le registry."""
        expected_scopes = ["users", "axes", "departments"]
        mock_registry = Mock()
        mock_registry.get_enabled_scopes.return_value = expected_scopes
        mock_get_registry.return_value = mock_registry

        # S'assurer que l'orchestrateur utilise le registry mocké
        self.orchestrator.registry = mock_registry

        self.orchestrator.args = Mock()
        self.orchestrator.args.scopes = []  # Aucun scope spécifique

        selected_scopes = self.orchestrator._get_selected_scopes()

        # Vérifier que les scopes retournés sont ceux attendus
        # Note: Le test vérifie que les scopes retournés correspondent aux scopes
        # attendus
        # même si l'ordre peut être différent
        self.assertEqual(set(selected_scopes), set(expected_scopes))

    @patch("core.orchestrator.ConfigLoader")
    def test_get_configuration_summary(self, mock_config_loader):
        """Test de récupération du résumé de configuration."""
        mock_config_loader.return_value.load.return_value = self.config

        summary = self.orchestrator.get_configuration_summary()

        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["config_file"], str(Path(self.temp_config_file.name)))
        self.assertFalse(summary["database_prod"])
        self.assertTrue(summary["api_sandbox"])


if __name__ == "__main__":
    unittest.main()
