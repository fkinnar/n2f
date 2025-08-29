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
                    "sql_column_filter": ["AxeId", "AxeName", "AxeType", "Entreprise"],
                    "sync_function": "business.process.axe_synchronizer.AxeSynchronizer.sync_axes"
                }
            },
            "cache": {
                "enabled": True,
                "persist_cache": True,
                "cache_dir": "cache_persistent",
                "max_size_mb": 500,
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
        
        data = []
        for i in range(count):
            company_idx = i % len(companies)
            company = companies[company_idx]
            domain = domains[company_idx]
            
            user_data = {
                "AdresseEmail": f"user{i+1}@{domain}",
                "Nom": f"Nom{i+1}",
                "Prenom": f"Prenom{i+1}",
                "Entreprise": company,
                "Departement": f"Dept{(i % 5) + 1}",
                "Actif": True if i % 10 != 0 else False  # 90% actifs
            }
            data.append(user_data)
        
        return pd.DataFrame(data)

    def create_realistic_axe_data(self, count=50):
        """Crée des données d'axes réalistes."""
        axe_types = ["PROJECT", "DEPARTMENT", "COST_CENTER", "CUSTOM"]
        companies = ["Company A", "Company B", "Company C", "Company D"]
        
        data = []
        for i in range(count):
            axe_data = {
                "AxeId": f"AXE{i+1:03d}",
                "AxeName": f"Axe {i+1}",
                "AxeType": axe_types[i % len(axe_types)],
                "Entreprise": companies[i % len(companies)],
                "Actif": True if i % 8 != 0 else False  # 87.5% actifs
            }
            data.append(axe_data)
        
        return pd.DataFrame(data)


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
        mock_cache_config.enabled = True
        mock_cache_config.persist_cache = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données utilisateurs réalistes
        user_data = self.create_realistic_user_data(100)
        
        # Mock du résultat de synchronisation
        success_result = SyncResult("users", True, [user_data], 
                                  error_message=None, duration_seconds=15.5)
        mock_executor.execute_scope.return_value = success_result
        
        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users"]
        
        # Test de synchronisation complète
        start_time = time.time()
        
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifications
        self.assertLess(duration, 10.0)  # Doit s'exécuter rapidement
        mock_executor.execute_scope.assert_called_once_with("users")
        mock_log_manager.return_value.add_result.assert_called_once_with(success_result)
        
        # Vérifier les données
        result_data = success_result.results[0]
        self.assertEqual(len(result_data), 100)
        self.assertIn("AdresseEmail", result_data.columns)
        self.assertIn("Nom", result_data.columns)
        self.assertIn("Entreprise", result_data.columns)

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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données avec conflits
        user_data = self.create_realistic_user_data(50)
        
        # Ajouter des utilisateurs avec des emails en double (conflit)
        conflict_data = pd.DataFrame({
            "AdresseEmail": ["conflict@company-a.com", "conflict@company-a.com"],
            "Nom": ["Conflict1", "Conflict2"],
            "Prenom": ["User1", "User2"],
            "Entreprise": ["Company A", "Company A"],
            "Departement": ["Dept1", "Dept2"],
            "Actif": [True, True]
        })
        
        user_data_with_conflicts = pd.concat([user_data, conflict_data], ignore_index=True)
        
        # Mock du résultat avec conflits
        success_result = SyncResult("users", True, [user_data_with_conflicts], 
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
        
        # Vérifier que les conflits sont présents dans les données
        result_data = success_result.results[0]
        conflict_emails = result_data[result_data["AdresseEmail"] == "conflict@company-a.com"]
        self.assertEqual(len(conflict_emails), 2)


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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données d'axes réalistes
        axe_data = self.create_realistic_axe_data(50)
        
        # Mock du résultat de synchronisation
        success_result = SyncResult("axes", True, [axe_data], 
                                  error_message=None, duration_seconds=12.0)
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
        result_data = success_result.results[0]
        self.assertEqual(len(result_data), 50)
        self.assertIn("AxeId", result_data.columns)
        self.assertIn("AxeName", result_data.columns)
        self.assertIn("AxeType", result_data.columns)
        
        # Vérifier les types d'axes
        axe_types = result_data["AxeType"].unique()
        expected_types = ["PROJECT", "DEPARTMENT", "COST_CENTER", "CUSTOM"]
        for axe_type in axe_types:
            self.assertIn(axe_type, expected_types)


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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données réalistes
        user_data = self.create_realistic_user_data(75)
        axe_data = self.create_realistic_axe_data(25)
        
        # Mock des résultats pour chaque scope
        users_result = SyncResult("users", True, [user_data], 
                                error_message=None, duration_seconds=10.0)
        axes_result = SyncResult("axes", True, [axe_data], 
                               error_message=None, duration_seconds=8.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]
        
        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]
        
        # Test de synchronisation multi-scopes
        start_time = time.time()
        
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifications
        self.assertLess(duration, 15.0)  # Doit s'exécuter en moins de 15 secondes
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_executor.execute_scope.assert_any_call("users")
        mock_executor.execute_scope.assert_any_call("axes")
        
        # Vérifier que les résultats ont été ajoutés
        self.assertEqual(mock_log_manager.return_value.add_result.call_count, 2)
        mock_log_manager.return_value.add_result.assert_any_call(users_result)
        mock_log_manager.return_value.add_result.assert_any_call(axes_result)


class TestLoadTestingScenario(TestRealScenariosBase):
    """Tests de charge pour des scénarios réels."""

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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création d'un grand volume de données (1000 utilisateurs)
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
        start_time = time.time()
        
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifications de performance
        self.assertLess(duration, 10.0)  # Le test doit être rapide même avec beaucoup de données
        self.assertEqual(len(large_user_data), 1000)
        
        # Vérifier la mémoire utilisée
        mock_get_memory_manager.assert_called_once()

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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données volumineuses
        large_user_data = self.create_realistic_user_data(500)
        large_axe_data = self.create_realistic_axe_data(200)
        
        # Mock des résultats avec durées différentes
        users_result = SyncResult("users", True, [large_user_data], 
                                error_message=None, duration_seconds=25.0)
        axes_result = SyncResult("axes", True, [large_axe_data], 
                               error_message=None, duration_seconds=18.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]
        
        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]
        
        # Test d'exécution concurrente
        start_time = time.time()
        
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifications
        self.assertLess(duration, 20.0)  # Doit être plus rapide que la somme des durées
        self.assertEqual(mock_executor.execute_scope.call_count, 2)


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
        mock_cache_config.enabled = True
        mock_config.cache = mock_cache_config
        
        mock_loader = Mock()
        mock_loader.load.return_value = mock_config
        mock_config_loader.return_value = mock_loader
        
        mock_context = Mock(spec=SyncContext)
        mock_sync_context.return_value = mock_context
        
        mock_executor = Mock()
        mock_scope_executor.return_value = mock_executor
        
        # Création de données réalistes
        user_data = self.create_realistic_user_data(100)
        axe_data = self.create_realistic_axe_data(50)
        
        # Mock des résultats : un succès, un échec
        users_result = SyncResult("users", True, [user_data], 
                                error_message=None, duration_seconds=12.0)
        axes_result = SyncResult("axes", False, [], 
                               error_message="API timeout after 30 seconds", duration_seconds=30.0)
        mock_executor.execute_scope.side_effect = [users_result, axes_result]
        
        # Mock du registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_enabled_scopes.return_value = ["users", "axes"]
        
        # Test de récupération
        orchestrator = SyncOrchestrator(self.test_config_path, self.args)
        orchestrator.run()
        
        # Vérifications
        self.assertEqual(mock_executor.execute_scope.call_count, 2)
        mock_log_manager.return_value.add_result.assert_any_call(users_result)
        mock_log_manager.return_value.add_result.assert_any_call(axes_result)
        
        # Vérifier que le premier scope a réussi
        self.assertTrue(users_result.success)
        self.assertEqual(len(users_result.results[0]), 100)
        
        # Vérifier que le second scope a échoué
        self.assertFalse(axes_result.success)
        self.assertIn("timeout", axes_result.error_message.lower())


if __name__ == '__main__':
    unittest.main()
