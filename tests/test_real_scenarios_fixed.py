"""
Tests d'intégration pour des scénarios réels de synchronisation N2F.

Ce module contient des tests qui simulent des scénarios réels d'utilisation
du système de synchronisation, avec des données réalistes et des cas d'usage
typiques.

Scénarios couverts :
- Synchronisation complète d'utilisateurs
- Synchronisation d'axes personnalisés
- Gestion des conflits de données
- Synchronisation incrémentale
- Récupération après panne
- Tests de charge
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
import time

# Ajout du chemin du projet pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from core.orchestrator import SyncOrchestrator, SyncResult
from core.config import SyncConfig, DatabaseConfig, ApiConfig, ScopeConfig, CacheConfig
from core.registry import SyncRegistry, RegistryEntry
from business.process.user_synchronizer import UserSynchronizer
from business.process.axe_synchronizer import AxeSynchronizer
from helper.context import SyncContext


class TestRealScenariosBase(unittest.TestCase):
    """Classe de base pour les tests de scénarios réels."""

    def setUp(self):
        """Configuration initiale pour les tests de scénarios réels."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.test_dir) / "test_real_scenarios.yaml"

        # Configuration de test réaliste
        self.create_realistic_test_config()

        # Arguments de test
        self.args = Mock(spec=argparse.Namespace)
        self.args.create = True
        self.args.update = True
        self.args.delete = False
        self.args.config = "test_real_scenarios"
        self.args.scope = ["users"]
        self.args.clear_cache = False
        self.args.invalidate_cache = None

        # Mock des variables d'environnement
        self.env_patcher = patch.dict(os.environ, {
            'AGRESSO_DB_USER': 'agresso_user',
            'AGRESSO_DB_PASSWORD': 'agresso_pass',
            'N2F_CLIENT_ID': 'n2f_client',
            'N2F_CLIENT_SECRET': 'n2f_secret'
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

    def create_realistic_test_config(self):
        """Crée une configuration de test réaliste."""
        config = {
            "database": {
                "host": "agresso-db.company.com",
                "port": 1433,
                "database": "AGRESSO_PROD",
                "timeout": 60
            },
            "api": {
                "base_url": "https://api.n2f.com",
                "timeout": 30,
                "max_retries": 5
            },
            "scopes": {
                "users": {
                    "enabled": True,
                    "display_name": "Utilisateurs",
                    "sql_filename": "get-agresso-n2f-users.prod.sql",
                    "sql_column_filter": ["AdresseEmail", "Nom", "Prenom", "Entreprise"],
                    "sync_function": "business.process.user_synchronizer.UserSynchronizer.sync_users"
                },
                "axes": {
                    "enabled": True,
                    "display_name": "Axes personnalisés",
                    "sql_filename": "get-agresso-n2f-customaxes.prod.sql",
                    "sql_column_filter": ["code", "name", "type"],
                    "sync_function": "business.process.axe_synchronizer.AxeSynchronizer.sync_axes"
                }
            },
            "cache": {
                "enabled": True,
                "persist_cache": False,
                "cache_dir": "cache",
                "max_size_mb": 200,
                "default_ttl": 7200
            },
            "memory_limit_mb": 2048
        }

        import yaml
        with open(self.test_config_path, 'w') as f:
            yaml.dump(config, f)

    def create_realistic_user_data(self, count=100):
        """Crée des données utilisateurs réalistes."""
        companies = ["Company A", "Company B", "Company C", "Company D"]
        domains = ["company-a.com", "company-b.com", "company-c.com", "company-d.com"]

        users = []
        for i in range(count):
            company_idx = i % len(companies)
            company = companies[company_idx]
            domain = domains[company_idx]

            user = {
                "AdresseEmail": f"user{i+1}@{domain}",
                "Nom": f"User{i+1}",
                "Prenom": f"FirstName{i+1}",
                "Entreprise": company,
                "Departement": f"Dept{(i % 5) + 1}",
                "Fonction": f"Role{(i % 3) + 1}"
            }
            users.append(user)

        return pd.DataFrame(users)

    def create_realistic_axe_data(self, count=50):
        """Crée des données d'axes réalistes."""
        axe_types = ["PROJECT", "COST_CENTER", "DEPARTMENT", "REGION"]

        axes = []
        for i in range(count):
            axe_type = axe_types[i % len(axe_types)]
            axe = {
                "code": f"{axe_type}_{i+1:03d}",
                "name": f"{axe_type} {i+1}",
                "type": axe_type,
                "description": f"Description for {axe_type} {i+1}",
                "active": True
            }
            axes.append(axe)

        return pd.DataFrame(axes)


class TestUserSynchronizationScenario(TestRealScenariosBase):
    """Tests de scénarios de synchronisation d'utilisateurs."""

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_full_user_synchronization_scenario(self, mock_log_manager, mock_scope_executor,
                                              mock_sync_context, mock_get_registry,
                                              mock_get_retry_manager, mock_get_metrics,
                                              mock_get_memory_manager, mock_get_cache,
                                              mock_config_loader, mock_load_dotenv):
        """Test de synchronisation complète d'utilisateurs (scénario réel)."""

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

        # Création de données utilisateurs réalistes
        user_data = self.create_realistic_user_data(50)

        # Mock du résultat de synchronisation
        success_result = SyncResult("users", True, [user_data],
                                  error_message=None, duration_seconds=15.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Test de synchronisation complète
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        mock_executor.execute_scope.assert_called_once_with("users")
        mock_log_manager.return_value.add_result.assert_called_once_with(success_result)

        # Vérifier les données
        self.assertEqual(len(user_data), 50)
        self.assertIn("AdresseEmail", user_data.columns)
        self.assertIn("Nom", user_data.columns)

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_user_synchronization_with_conflicts(self, mock_log_manager, mock_scope_executor,
                                               mock_sync_context, mock_get_registry,
                                               mock_get_retry_manager, mock_get_metrics,
                                               mock_get_memory_manager, mock_get_cache,
                                               mock_config_loader, mock_load_dotenv):
        """Test de synchronisation d'utilisateurs avec conflits de données."""

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

        # Création de données avec conflits
        user_data = self.create_realistic_user_data(20)
        # Ajouter des doublons pour simuler des conflits
        duplicate_user = user_data.iloc[0].copy()
        duplicate_user["Nom"] = "Modified Name"
        user_data = pd.concat([user_data, pd.DataFrame([duplicate_user])], ignore_index=True)

        # Mock du résultat avec conflits
        success_result = SyncResult("users", True, [user_data],
                                  error_message=None, duration_seconds=8.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Test de synchronisation avec conflits
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        mock_executor.execute_scope.assert_called_once_with("users")

        # Vérifier la gestion des conflits
        self.assertEqual(len(user_data), 21)  # 20 + 1 doublon


class TestAxeSynchronizationScenario(TestRealScenariosBase):
    """Tests de scénarios de synchronisation d'axes."""

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_full_axe_synchronization_scenario(self, mock_log_manager, mock_scope_executor,
                                             mock_sync_context, mock_get_registry,
                                             mock_get_retry_manager, mock_get_metrics,
                                             mock_get_memory_manager, mock_get_cache,
                                             mock_config_loader, mock_load_dotenv):
        """Test de synchronisation complète d'axes (scénario réel)."""

        # Configuration pour les axes
        self.args.scope = ["axes"]

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

        # Création de données d'axes réalistes
        axe_data = self.create_realistic_axe_data(30)

        # Mock du résultat de synchronisation
        success_result = SyncResult("axes", True, [axe_data],
                                  error_message=None, duration_seconds=10.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["axes"]

        # Test de synchronisation complète
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        mock_executor.execute_scope.assert_called_once_with("axes")
        mock_log_manager.return_value.add_result.assert_called_once_with(success_result)

        # Vérifier les données
        self.assertEqual(len(axe_data), 30)
        self.assertIn("code", axe_data.columns)
        self.assertIn("name", axe_data.columns)


class TestMultiScopeSynchronizationScenario(TestRealScenariosBase):
    """Tests de scénarios de synchronisation multi-scopes."""

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_multi_scope_synchronization_scenario(self, mock_log_manager, mock_scope_executor,
                                                mock_sync_context, mock_get_registry,
                                                mock_get_retry_manager, mock_get_metrics,
                                                mock_get_memory_manager, mock_get_cache,
                                                mock_config_loader, mock_load_dotenv):
        """Test de synchronisation multi-scopes (scénario réel)."""

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

        # Création de données réalistes
        user_data = self.create_realistic_user_data(25)
        axe_data = self.create_realistic_axe_data(15)

        # Mock des résultats pour chaque scope
        users_result = SyncResult("users", True, [user_data],
                                error_message=None, duration_seconds=12.0)
        axes_result = SyncResult("axes", True, [axe_data],
                               error_message=None, duration_seconds=8.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Test de synchronisation multi-scopes
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_executor.execute_scope.assert_any_call("users")
        mock_executor.execute_scope.assert_any_call("axes")

        # Vérifier que les résultats ont été ajoutés
        self.assertEqual(mock_log_manager.return_value.add_result.call_count, 2)


class TestLoadTestingScenario(TestRealScenariosBase):
    """Tests de scénarios de charge."""

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_large_scale_user_synchronization(self, mock_log_manager, mock_scope_executor,
                                            mock_sync_context, mock_get_registry,
                                            mock_get_retry_manager, mock_get_metrics,
                                            mock_get_memory_manager, mock_get_cache,
                                            mock_config_loader, mock_load_dotenv):
        """Test de charge avec un grand volume d'utilisateurs."""

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

        # Création d'un grand volume de données
        large_user_data = self.create_realistic_user_data(1000)

        # Mock du résultat avec grand volume
        success_result = SyncResult("users", True, [large_user_data],
                                  error_message=None, duration_seconds=45.0)
        mock_executor.execute_scope.return_value = success_result

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]

        # Test de charge
        start_time = datetime.now()

        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Vérifications de performance
        self.assertLess(duration, 10.0)  # Doit s'exécuter en moins de 10 secondes
        self.assertEqual(len(large_user_data), 1000)  # Vérifier le volume de données

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_concurrent_scope_execution(self, mock_log_manager, mock_scope_executor,
                                      mock_sync_context, mock_get_registry,
                                      mock_get_retry_manager, mock_get_metrics,
                                      mock_get_memory_manager, mock_get_cache,
                                      mock_config_loader, mock_load_dotenv):
        """Test d'exécution concurrente de plusieurs scopes."""

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

        # Création de données de test
        user_data = self.create_realistic_user_data(100)
        axe_data = self.create_realistic_axe_data(50)

        # Mock des résultats avec timing réaliste
        users_result = SyncResult("users", True, [user_data],
                                error_message=None, duration_seconds=20.0)
        axes_result = SyncResult("axes", True, [axe_data],
                               error_message=None, duration_seconds=15.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Test d'exécution concurrente
        start_time = datetime.now()

        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        self.assertLess(total_duration, 5.0)  # L'exécution totale doit être rapide


class TestErrorRecoveryScenario(TestRealScenariosBase):
    """Tests de scénarios de récupération d'erreur."""

    @patch('core.orchestrator.load_dotenv')
    @patch('core.orchestrator.ConfigLoader')
    @patch('core.orchestrator.get_cache')
    @patch('core.orchestrator.get_memory_manager')
    @patch('core.orchestrator.get_metrics')
    @patch('core.orchestrator.get_retry_manager')
    @patch('core.orchestrator.get_registry')
    @patch('core.orchestrator.SyncContext')
    @patch('core.orchestrator.ScopeExecutor')
    @patch('core.orchestrator.LogManager')
    def test_partial_failure_with_recovery(self, mock_log_manager, mock_scope_executor,
                                         mock_sync_context, mock_get_registry,
                                         mock_get_retry_manager, mock_get_metrics,
                                         mock_get_memory_manager, mock_get_cache,
                                         mock_config_loader, mock_load_dotenv):
        """Test de récupération après échec partiel (scénario réel)."""

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

        # Création de données de test
        user_data = self.create_realistic_user_data(30)

        # Mock des résultats : un succès, un échec
        success_result = SyncResult("users", True, [user_data],
                                  error_message=None, duration_seconds=10.0)
        failure_result = SyncResult("axes", False, [],
                                  error_message="API Error - Rate limit exceeded",
                                  duration_seconds=5.0)
        mock_executor.execute_scope.side_effect = [success_result, failure_result]

        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]

        # Test de récupération
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()

        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_log_manager.return_value.add_result.assert_any_call(success_result)
        mock_log_manager.return_value.add_result.assert_any_call(failure_result)

        # Vérifier que le premier scope a réussi malgré l'échec du second
        self.assertTrue(success_result.success)
        self.assertFalse(failure_result.success)


if __name__ == '__main__':
    unittest.main()
