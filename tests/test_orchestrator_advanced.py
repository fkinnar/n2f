#!/usr/bin/env python3
"""
Tests avanc\3s pour le module src/core/orchestrator.py.

Ce module teste les fonctionnalit\3s avanc\3es de l'orchestrateur.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Ajouter le r\3pertoire python au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

# Imports apr\3s modification du path
from core.orchestrator import SyncOrchestrator, LogManager, SyncResult
from core.config import SyncConfig, DatabaseConfig, ApiConfig, CacheConfig
from core.registry import SyncRegistry
from core import SyncContext
from core.exceptions import SyncException


class TestSyncOrchestratorAdvanced(unittest.TestCase):
    """Tests avanc\3s pour SyncOrchestrator."""

    def setUp(self):
        """Configuration initiale."""
        # Cr\3er une configuration de test
        self.config = SyncConfig(
            database=DatabaseConfig(prod=False),
            api=ApiConfig(
                base_urls="https://test.api.com", sandbox=True, simulate=False
            ),
            scopes={},
            cache=CacheConfig(enabled=True, default_ttl=3600, max_size_mb=100),
        )

        # Cr\3er un fichier de configuration temporaire
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

        # Cr\3er l'orchestrator
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
        """Test d'ex\3cution avec des scopes sp\3cifiques."""
        # Configuration des mocks
        mock_config_loader.return_value.load.return_value = self.config
        mock_registry.return_value.get_enabled_scopes.return_value = ["users", "axes"]
        mock_context.return_value = Mock()
        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        # Simuler un r\3sultat de succ\3s
        success_result = SyncResult(
            scope_name="users",
            success=True,
            duration_seconds=1.0,
            error_message="",
            results=[],
        )
        mock_executor_instance.execute_scope.return_value = success_result

        # Configurer les arguments pour des scopes sp\3cifiques
        self.orchestrator.args = Mock()
        self.orchestrator.args.scope = ["users"]
        self.orchestrator.args.invalidate_cache = None  # Pas d'invalidation de cache

        # Ex\3cuter
        self.orchestrator.run()

        # V\3rifications
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
        """Test d'ex\3cution avec erreur lors de l'ex\3cution d'un scope."""
        # Configuration des mocks
        mock_config_loader.return_value.load.return_value = self.config
        mock_registry.return_value.get_enabled_scopes.return_value = ["users"]
        mock_context.return_value = Mock()
        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        # Simuler une exception lors de l'ex\3cution
        mock_executor_instance.execute_scope.side_effect = SyncException(
            "Scope execution error"
        )

        # Configurer les arguments
        self.orchestrator.args = Mock()
        self.orchestrator.args.scope = ["users"]
        self.orchestrator.args.invalidate_cache = None  # Pas d'invalidation de cache

        # Ex\3cuter et v\3rifier que l'exception est lev\3e
        with self.assertRaises(SyncException):
            self.orchestrator.run()

        # V\3rifier que end_operation a \3t\3 appel\3 avec success=False
        mock_end_operation.assert_called_once()
        call_args = mock_end_operation.call_args[1]
        self.assertFalse(call_args["success"])
        self.assertEqual(call_args["error_message"], "Scope execution error")

    def test_get_selected_scopes_with_specific_scopes(self):
        """Test de s\3lection des scopes avec des scopes sp\3cifiques."""
        self.orchestrator.args = Mock()
        self.orchestrator.args.scope = ["users", "axes"]

        selected_scopes = self.orchestrator._get_selected_scopes()

        # L'ordre n'est pas important, v\3rifier seulement que les deux scopes sont
        # pr\3sents
        self.assertEqual(set(selected_scopes), {"users", "axes"})

    @patch("core.orchestrator.get_registry")
    def test_get_selected_scopes_from_registry(self, mock_get_registry):
        """Test de s\3lection des scopes depuis le registry."""
        expected_scopes = ["users", "axes", "departments"]
        mock_registry = Mock()
        mock_registry.get_enabled_scopes.return_value = expected_scopes
        mock_get_registry.return_value = mock_registry

        # S'assurer que l'orchestrateur utilise le registry mock\3
        self.orchestrator.registry = mock_registry

        self.orchestrator.args = Mock()
        self.orchestrator.args.scope = []  # Aucun scope sp\3cifique

        selected_scopes = self.orchestrator._get_selected_scopes()

        # V\3rifier que les scopes retourn\3s sont ceux attendus
        # Note: Le test v\3rifie que les scopes retourn\3s correspondent aux scopes
        # attendus
        # m\3me si l'ordre peut \3tre diff\3rent
        self.assertEqual(set(selected_scopes), set(expected_scopes))

    @patch("core.orchestrator.ConfigLoader")
    def test_get_configuration_summary(self, mock_config_loader):
        """Test de r\3cup\3ration du r\3sum\3 de configuration."""
        mock_config_loader.return_value.load.return_value = self.config

        summary = self.orchestrator.get_configuration_summary()

        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["config_file"], str(Path(self.temp_config_file.name)))
        self.assertFalse(summary["database_prod"])
        self.assertTrue(summary["api_sandbox"])


if __name__ == "__main__":
    unittest.main()
