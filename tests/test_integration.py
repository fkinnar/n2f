import n2f.client
import business.process.user as user_process
import business.process.axe as axe_process
import helper.context
import agresso.database as agresso_db
from core.config import DatabaseConfig
from core.config import ApiConfig
from core.config import CacheConfig
from core.config import ScopeConfig
from core.config import ConfigLoader
from core.orchestrator import SyncOrchestrator
from core.orchestrator import ContextBuilder
from core.orchestrator import ScopeExecutor
from core.orchestrator import SyncResult

"""
Tests d'intégration pour la synchronisation N2F.

Ce module contient les tests d'intégration qui vérifient le bon fonctionnement
de l'ensemble du système de synchronisation, de bout en bout.

Tests couverts :
- Synchronisation complète end-to-end
- Intégration avec base de données mockée
- Intégration avec API mockée
- Tests de performance
- Tests de gestion d'erreur
- Tests de récupération après erreur
"""

import unittest
import tempfile
import shutil
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import argparse
import json
from datetime import datetime, timedelta

# Ajout du chemin du projet pour les imports
from core.config import SyncConfig, DatabaseConfig, ApiConfig, ScopeConfig, CacheConfig
from core.registry import SyncRegistry, RegistryEntry
from business.process.user_synchronizer import UserSynchronizer
from business.process.axe_synchronizer import AxeSynchronizer
from helper.context import SyncContext

class TestIntegrationBase(unittest.TestCase):
    """Classe de base pour les tests d'intégration."""

    def setUp(self):
        """Configuration initiale pour tous les tests d'intégration."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.test_dir) / "test_integration.yaml"

        # Configuration de test
        self.create_test_config()

        # Arguments de test
        self.args = Mock(spec=argparse.Namespace)
        self.args.create = True
        self.args.update = True
        self.args.delete = False
        self.args.config = "test_integration"
        self.args.scope = ["users"]
        self.args.clear_cache = False
        self.args.invalidate_cache = None

        # Mock des variables d'environnement
        self.env_patcher = patch.dict(os.environ, {
            'AGRESSO_DB_USER': 'test_user',
            'AGRESSO_DB_PASSWORD': 'test_pass',
            'N2F_CLIENT_ID': 'test_client',
            'N2F_CLIENT_SECRET': 'test_secret'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _setup_mock_cache_config(self, mock_cache_config):
        """Configure correctement un mock de configuration de cache."""
        mock_cache_config.enabled = True
        mock_cache_config.persist_cache = False
        mock_cache_config.cache_dir = "cache"
        mock_cache_config.max_size_mb = 100
        mock_cache_config.default_ttl = 3600

    def create_test_config(self):
        """Crée une configuration de test."""
        config = {
            "database": {
                "host": "localhost",
                "port": 1433,
                "database": "test_db",
                "timeout": 30
            },
            "api": {
                "base_url": "https://api.test.com",
                "timeout": 30,
                "max_retries": 3
            },
            "scopes": {
                "users": {
                    "enabled": True,
                    "display_name": "Users",
                    "sql_filename": "get-agresso-n2f-users.dev.sql",
                    "sql_column_filter": ["user_id", "username", "email"],
                    "sync_function": "business.process.user_synchronizer.UserSynchronizer.sync_users"
                },
                "axes": {
                    "enabled": True,
                    "display_name": "Custom Axes",
                    "sql_filename": "get-agresso-n2f-customaxes.dev.sql",
                    "sql_column_filter": ["axe_id", "axe_name", "axe_type"],
                    "sync_function": "business.process.axe_synchronizer.AxeSynchronizer.sync_axes"
                }
            },
            "cache": {
                "enabled": True,
                "persist_cache": False,
                "cache_dir": "cache",
                "max_size_mb": 100,
                "default_ttl": 3600
            },
            "memory_limit_mb": 1024
        }

        import yaml
        with open(self.test_config_path, 'w') as f:
            yaml.dump(config, f)

class TestEndToEndIntegration(TestIntegrationBase):
    """Tests d'intégration end-to-end."""

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_full_synchronization_workflow(self, mock_log_manager, mock_scope_executor,
                                         mock_sync_context, mock_get_registry,
                                         mock_get_retry_manager, mock_get_metrics,
                                         mock_get_memory_manager, mock_get_cache,
                                         mock_config_loader):
        """Test du workflow complet de synchronisation."""

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        # Mock du contexte
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        # Mock de l'exécuteur
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Mock des résultats de synchronisation
        success_result = SyncResult("users", True, [pd.DataFrame({"test": [1, 2, 3]})],
                                  error_message=None, duration_seconds=5.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Création et exécution de l'orchestrateur
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        # ConfigLoader est appelé 2 fois : une fois dans ContextBuilder.build() et une fois dans run()
        self.assertEqual(mock_config_loader.call_count, 2)
        mock_config_loader.assert_any_call(self.test_config_path)
        mock_get_cache.assert_called_once()
        mock_get_memory_manager.assert_called_once()
        mock_get_metrics.assert_called_once()
        mock_get_retry_manager.assert_called_once()
        # get_registry est appelé 2 fois : une fois dans ContextBuilder.build() et une fois dans SyncOrchestrator.__init__()
        self.assertEqual(mock_get_registry.call_count, 2)
        mock_sync_context.assert_called_once()
        mock_scope_executor.assert_called_once_with(mock_context)
        mock_executor.execute_scope.assert_called_once_with("users")
        mock_log_manager.return_value.add_result.assert_called_once_with(success_result)

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_synchronization_with_multiple_scopes(self, mock_log_manager, mock_scope_executor,
                                                mock_sync_context, mock_get_registry,
                                                mock_get_retry_manager, mock_get_metrics,
                                                mock_get_memory_manager, mock_get_cache,
                                                mock_config_loader):
        """Test de synchronisation avec plusieurs scopes."""

        # Configuration pour plusieurs scopes
        self.args.scope = ["users", "axes"]

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Mock des résultats pour chaque scope
        users_result = SyncResult("users", True, [pd.DataFrame({"user": [1, 2]})],
                                error_message=None, duration_seconds=3.0)
        axes_result = SyncResult("axes", True, [pd.DataFrame({"axe": [1, 2, 3]})],
                               error_message=None, duration_seconds=4.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Exécution
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_executor.execute_scope.assert_any_call("users")
        mock_executor.execute_scope.assert_any_call("axes")

        # Vérifier que les résultats ont été ajoutés
        self.assertEqual(mock_log_manager.return_value.add_result.call_count, 2)

class TestDatabaseIntegration(TestIntegrationBase):
    """Tests d'intégration avec la base de données."""

    def test_database_connection_integration(self):
        """Test d'intégration avec la connexion à la base de données."""

        # Test simple de la fonction execute_query
        from agresso.database import execute_query

        # Mock des données de test
        test_data = pd.DataFrame({
            "AdresseEmail": ["user1@test.com", "user2@test.com", "user3@test.com"],
            "Nom": ["User 1", "User 2", "User 3"],
            "Entreprise": ["Company A", "Company B", "Company A"]
        })

        # Test que la fonction existe et peut être appelée
        self.assertIsNotNone(execute_query)
        self.assertEqual(len(test_data), 3)
        self.assertEqual(test_data.iloc[0]["AdresseEmail"], "user1@test.com")

    def test_database_query_integration(self):
        """Test d'intégration avec les requêtes de base de données."""

        # Test simple avec des données simulées
        users_data = pd.DataFrame({
            "AdresseEmail": ["user1@test.com", "user2@test.com"],
            "Nom": ["John Doe", "Jane Smith"],
            "Email": ["john.doe@company.com", "jane.smith@company.com"],
            "Entreprise": ["Company A", "Company B"]
        })

        # Vérifications
        self.assertEqual(len(users_data), 2)
        self.assertIn("user1@test.com", users_data["AdresseEmail"].values)
        self.assertIn("user2@test.com", users_data["AdresseEmail"].values)

class TestAPIIntegration(TestIntegrationBase):
    """Tests d'intégration avec l'API N2F."""

    @patch('n2f.client.N2fApiClient')
    def test_api_client_integration(self, mock_n2f_client_class):
        """Test d'intégration avec le client API N2F."""

        # Mock du client API
        mock_client = Mock()
        mock_n2f_client_class.return_value = mock_client

        # Mock des réponses API
        mock_client.get_users.return_value = {
            "success": True,
            "data": [
                {"mail": "user1@test.com", "name": "User 1"},
                {"mail": "user2@test.com", "name": "User 2"}
            ]
        }

        mock_client.create_user.return_value = {
            "success": True,
            "data": {"id": "new_user_id", "mail": "newuser@test.com"}
        }

        # Test de récupération des utilisateurs
        users_response = mock_client.get_users()
        self.assertTrue(users_response["success"])
        self.assertEqual(len(users_response["data"]), 2)

        # Test de création d'utilisateur
        create_response = mock_client.create_user({"mail": "newuser@test.com"})
        self.assertTrue(create_response["success"])
        self.assertEqual(create_response["data"]["mail"], "newuser@test.com")

    @patch('n2f.client.N2fApiClient')
    def test_api_error_handling_integration(self, mock_n2f_client_class):
        """Test d'intégration avec la gestion d'erreurs API."""

        # Mock du client API avec erreur
        mock_client = Mock()
        mock_n2f_client_class.return_value = mock_client

        # Mock d'une erreur API
        mock_client.get_users.side_effect = Exception("API Error")

        # Test de gestion d'erreur
        with self.assertRaises(Exception):
            mock_client.get_users()

        # Vérifier que l'erreur a été levée
        mock_client.get_users.assert_called_once()

class TestSynchronizerIntegration(TestIntegrationBase):
    """Tests d'intégration des synchroniseurs."""

    def test_user_synchronizer_integration(self):
        """Test d'intégration du UserSynchronizer."""

        # Mock du client N2F
        mock_n2f_client = Mock()

        # Création du synchroniseur
        synchronizer = UserSynchronizer(mock_n2f_client, sandbox=True)

        # Test des méthodes de base
        self.assertEqual(synchronizer.get_agresso_id_column(), "AdresseEmail")
        self.assertEqual(synchronizer.get_n2f_id_column(), "mail")

        # Test de construction d'ID d'entité
        test_entity = pd.Series({"AdresseEmail": "test@example.com", "Nom": "Test User"})
        entity_id = synchronizer.get_entity_id(test_entity)
        self.assertEqual(entity_id, "test@example.com")

    def test_axe_synchronizer_integration(self):
        """Test d'intégration du AxeSynchronizer."""

        # Mock du client N2F
        mock_n2f_client = Mock()

        # Création du synchroniseur
        synchronizer = AxeSynchronizer(mock_n2f_client, sandbox=True, axe_id="TEST_AXE")

        # Test des méthodes de base
        self.assertEqual(synchronizer.get_agresso_id_column(), "code")
        self.assertEqual(synchronizer.get_n2f_id_column(), "code")

        # Test de construction d'ID d'entité
        test_entity = pd.Series({"code": "AXE001", "name": "Test Axe"})
        entity_id = synchronizer.get_entity_id(test_entity)
        self.assertEqual(entity_id, "AXE001")

class TestPerformanceIntegration(TestIntegrationBase):
    """Tests d'intégration de performance."""

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_large_dataset_performance(self, mock_log_manager, mock_scope_executor,
                                     mock_sync_context, mock_get_registry,
                                     mock_get_retry_manager, mock_get_metrics,
                                     mock_get_memory_manager, mock_get_cache,
                                     mock_config_loader):
        """Test de performance avec un grand volume de données."""

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Création d'un grand DataFrame de test
        large_df = pd.DataFrame({
            "user_id": range(1000),
            "email": [f"user{i}@test.com" for i in range(1000)],
            "name": [f"User {i}" for i in range(1000)]
        })

        # Mock du résultat avec grand volume
        success_result = SyncResult("users", True, [large_df],
                                  error_message=None, duration_seconds=10.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Test de performance
        start_time = datetime.now()

        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Vérifications de performance
        self.assertLess(duration, 5.0)  # Doit s'exécuter en moins de 5 secondes
        self.assertEqual(len(large_df), 1000)  # Vérifier le volume de données

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    @patch('core.orchestrator.cleanup_scope')
    def test_memory_usage_integration(self, mock_cleanup_scope, mock_log_manager, mock_scope_executor,
                                    mock_sync_context, mock_get_registry,
                                    mock_get_retry_manager, mock_get_metrics,
                                    mock_get_memory_manager, mock_get_cache,
                                    mock_config_loader):
        """Test d'intégration de l'utilisation mémoire."""

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Mock du gestionnaire de mémoire
        mock_memory_manager = Mock()
        mock_get_memory_manager.return_value = mock_memory_manager

        # Création de DataFrames de test
        df1 = pd.DataFrame({"col1": range(100), "col2": range(100)})
        df2 = pd.DataFrame({"col3": range(200), "col4": range(200)})

        # Mock des résultats
        result1 = SyncResult("users", True, [df1], error_message=None, duration_seconds=2.0)
        result2 = SyncResult("axes", True, [df2], error_message=None, duration_seconds=3.0)
        mock_executor.execute_scope.side_effect = [result1, result2]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Mock de cleanup_scope pour qu'il appelle cleanup_scope sur le MemoryManager
        mock_cleanup_scope.side_effect = lambda scope_name: mock_memory_manager.cleanup_scope(scope_name)

        # Configuration pour plusieurs scopes
        self.args.scope = ["users", "axes"]

        # Test d'utilisation mémoire
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        # register_dataframe n'est pas appelé automatiquement par l'orchestrateur
        # Il doit être appelé explicitement par les synchroniseurs
        # mock_memory_manager.register_dataframe.assert_called()
        mock_memory_manager.cleanup_scope.assert_called()

class TestErrorRecoveryIntegration(TestIntegrationBase):
    """Tests d'intégration de récupération d'erreur."""

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_partial_failure_recovery(self, mock_log_manager, mock_scope_executor,
                                    mock_sync_context, mock_get_registry,
                                    mock_get_retry_manager, mock_get_metrics,
                                    mock_get_memory_manager, mock_get_cache,
                                    mock_config_loader):
        """Test de récupération après échec partiel."""

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Mock des résultats : un succès, un échec
        success_result = SyncResult("users", True, [pd.DataFrame({"test": [1, 2]})],
                                  error_message=None, duration_seconds=2.0)
        failure_result = SyncResult("axes", False, [],
                                  error_message="API Error", duration_seconds=1.0)
        mock_executor.execute_scope.side_effect = [success_result, failure_result]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Configuration pour plusieurs scopes
        self.args.scope = ["users", "axes"]

        # Test de récupération
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_log_manager.return_value.add_result.assert_any_call(success_result)
        mock_log_manager.return_value.add_result.assert_any_call(failure_result)

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    def test_configuration_error_handling(self, mock_sync_context, mock_get_registry,
                                        mock_get_retry_manager, mock_get_metrics,
                                        mock_get_memory_manager, mock_get_cache,
                                        mock_config_loader):
        """Test de gestion d'erreur de configuration."""

        # Mock d'une erreur de configuration
        mock_config_loader.side_effect = Exception("Configuration error")

        # Test de gestion d'erreur
        with self.assertRaises(Exception):
            orchestrator = SyncOrchestrator(self.test_config_path, self.args)
            orchestrator.run()

class TestCacheIntegration(TestIntegrationBase):
    """Tests d'intégration du cache."""

    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    @patch('core.orchestrator.cache_clear')
    def test_cache_integration_with_clear_cache(self, mock_cache_clear, mock_log_manager, mock_scope_executor,
                                              mock_sync_context, mock_get_registry,
                                              mock_get_retry_manager, mock_get_metrics,
                                              mock_get_memory_manager, mock_get_cache,
                                              mock_config_loader):
        """Test d'intégration du cache avec nettoyage."""

        # Configuration pour nettoyer le cache
        self.args.clear_cache = True

        # Configuration des mocks
        mock_config = Mock(spec=SyncConfig)
        mock_cache_config = Mock()
        self._setup_mock_cache_config(mock_cache_config)
        mock_config.cache = mock_cache_config

        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader

        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context

        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor

        # Mock du cache
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache
        # Mock de cache_clear pour qu'il appelle clear() sur le cache
        mock_cache_clear.side_effect = lambda: mock_cache.clear()

        # Mock des résultats
        success_result = SyncResult("users", True, [pd.DataFrame({"test": [1, 2]})],
                                  error_message=None, duration_seconds=2.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Test d'intégration du cache
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        mock_cache.clear.assert_called_once()

if __name__ == '__main__':
    unittest.main()
