#!/usr/bin/env python3
"""
Tests pour la simulation avec données de production.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from core import SyncContext
from n2f.production_simulation import ProductionDataSimulator, SimulationMode
from n2f.real_data_tester import RealDataSyncTester, create_test_context


class TestProductionDataSimulator(unittest.TestCase):
    """Test du simulateur de données de production."""

    def setUp(self):
        """Configuration des tests."""
        self.context = create_test_context()
        self.simulator = ProductionDataSimulator(self.context, SimulationMode.REAL_DATA)

    @patch("n2f.production_simulation.select")
    def test_get_real_agresso_data(self, mock_select):
        """Test de récupération des vraies données Agresso."""
        # Mock des données Agresso
        mock_users_df = pd.DataFrame(
            {
                "email": ["user1@test.com", "user2@test.com"],
                "firstName": ["User1", "User2"],
                "lastName": ["Test1", "Test2"],
                "active": [True, True],
            }
        )

        mock_axes_df = pd.DataFrame(
            {
                "code": ["AXE001", "AXE002"],
                "name": ["Axe 1", "Axe 2"],
                "type": ["PROJECT", "PLATE"],
                "active": [True, True],
            }
        )

        mock_select.side_effect = [mock_users_df, mock_axes_df]

        # Test
        result = self.simulator._get_real_agresso_data()

        # Vérifications
        self.assertIn("users", result)
        self.assertIn("axes", result)
        self.assertEqual(len(result["users"]), 2)
        self.assertEqual(len(result["axes"]), 2)
        self.assertEqual(mock_select.call_count, 2)

    @patch("n2f.production_simulation.N2fApiClient")
    def test_get_simulated_n2f_data(self, mock_client_class):
        """Test de récupération des données N2F simulées."""
        # Mock du client N2F
        mock_client = Mock()
        mock_client.get_users.return_value = pd.DataFrame({"id": ["1", "2"]})
        mock_client.get_companies.return_value = pd.DataFrame({"id": ["1", "2"]})
        mock_client.get_roles.return_value = pd.DataFrame({"id": ["1", "2"]})
        mock_client.get_userprofiles.return_value = pd.DataFrame({"id": ["1", "2"]})
        mock_client_class.return_value = mock_client

        # Remplace le client du simulateur
        self.simulator.client = mock_client

        # Test
        result = self.simulator._get_simulated_n2f_data()

        # Vérifications
        self.assertIn("users", result)
        self.assertIn("companies", result)
        self.assertIn("roles", result)
        self.assertIn("profiles", result)
        self.assertEqual(len(result["users"]), 2)
        self.assertEqual(len(result["companies"]), 2)

    def test_simulate_full_sync(self):
        """Test de simulation complète."""
        with (
            patch.object(self.simulator, "_get_real_agresso_data") as mock_agresso,
            patch.object(self.simulator, "_get_simulated_n2f_data") as mock_n2f,
            patch.object(self.simulator, "_normalize_data") as mock_normalize,
            patch.object(self.simulator, "_simulate_synchronization") as mock_sync,
        ):

            # Mock des données
            mock_agresso.return_value = {
                "users": pd.DataFrame(),
                "axes": pd.DataFrame(),
            }
            mock_n2f.return_value = {
                "users": pd.DataFrame(),
                "companies": pd.DataFrame(),
            }
            mock_normalize.return_value = {"agresso_users": pd.DataFrame()}
            mock_sync.return_value = {"users": {}, "axes": {}}

            # Test
            result = self.simulator.simulate_full_sync()

            # Vérifications
            self.assertIn("simulation_mode", result)
            self.assertIn("statistics", result)
            self.assertIn("results", result)
            self.assertEqual(result["simulation_mode"], "real_data")


class TestRealDataSyncTester(unittest.TestCase):
    """Test du testeur de synchronisation avec données réelles."""

    def setUp(self):
        """Configuration des tests."""
        self.context = create_test_context()
        self.tester = RealDataSyncTester(self.context)

    @patch("n2f.real_data_tester.ProductionDataSimulator")
    def test_run_full_test(self, mock_simulator_class):
        """Test d'exécution complète."""
        # Mock du simulateur
        mock_simulator = Mock()
        mock_simulator.simulate_full_sync.return_value = {
            "simulation_mode": "real_data",
            "statistics": {"errors": 0, "users_processed": 10},
            "summary": {"success_rate": 95.0},
        }
        mock_simulator_class.return_value = mock_simulator

        # Test
        result = self.tester.run_full_test(SimulationMode.REAL_DATA)

        # Vérifications
        self.assertIn("test_mode", result)
        self.assertIn("simulation_results", result)
        self.assertIn("validation", result)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["test_mode"], "real_data")

    def test_validate_results(self):
        """Test de validation des résultats."""
        # Données de test
        results = {
            "statistics": {"errors": 0, "users_processed": 10, "axes_processed": 5},
            "summary": {"success_rate": 95.0},
        }

        # Test
        validation = self.tester._validate_results(results)

        # Vérifications
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["issues"]), 0)
        self.assertEqual(len(validation["warnings"]), 0)

    def test_validate_results_with_errors(self):
        """Test de validation avec erreurs."""
        # Données de test avec erreurs (aucun succès)
        results = {
            "statistics": {"errors": 5, "users_processed": 0, "axes_processed": 0},
            "summary": {"success_rate": 0.0},
        }

        # Test
        validation = self.tester._validate_results(results)

        # Vérifications
        self.assertFalse(validation["is_valid"])
        self.assertGreater(len(validation["issues"]), 0)
        self.assertGreater(len(validation["warnings"]), 0)


class TestCreateTestContext(unittest.TestCase):
    """Test de création du contexte de test."""

    def test_create_test_context_default(self):
        """Test de création avec paramètres par défaut."""
        context = create_test_context()

        self.assertIsInstance(context, SyncContext)
        self.assertEqual(context.client_id, "test_client")
        self.assertEqual(context.client_secret, "test_secret")
        self.assertTrue(context.get_config_value("n2f")["simulate"])

    def test_create_test_context_custom(self):
        """Test de création avec paramètres personnalisés."""
        context = create_test_context(
            base_dir="custom_test", db_user="custom_user", db_password="custom_pass"
        )

        self.assertEqual(str(context.base_dir), "custom_test")
        self.assertEqual(context.db_user, "custom_user")
        self.assertEqual(context.db_password, "custom_pass")


if __name__ == "__main__":
    unittest.main()
