#!/usr/bin/env python3
"""
Tests unitaires pour le module src/business/process/user.py.

Ce module teste les fonctions de synchronisation des utilisateurs.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys
import pandas as pd
import numpy as np

# Ajouter le répertoire python au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

# Imports après modification du path
import business.process.user as user_process
from core import SyncContext


class TestBusinessUser(unittest.TestCase):
    """Tests pour le module business.process.user."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Mock des arguments
        self.mock_args = Mock()
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True

        # Mock du contexte
        self.mock_context = Mock(spec=SyncContext)
        self.mock_context.get_config_value.return_value = {
            "sql-path": "path/to/sql",
            "prod": False,
        }
        self.mock_context.client_id = "test_client_id"
        self.mock_context.client_secret = "test_client_secret"
        self.mock_context.base_dir = "/test/base/dir"
        self.mock_context.db_user = "test_db_user"
        self.mock_context.db_password = "test_db_password"
        self.mock_context.args = self.mock_args

        # Mock du client N2F
        self.mock_n2f_client = Mock()

        # Mock des configurations
        self.mock_agresso_config = {"database": "agresso_db"}
        self.mock_n2f_config = {
            "base_urls": "https://test.n2f.com/api",
            "simulate": False,
            "sandbox": True,
        }

        # DataFrames de test
        self.df_agresso_users = pd.DataFrame(
            {
                "AdresseEmail": ["user1@test.com", "user2@test.com"],
                "Nom": ["User1", "User2"],
                "Prenom": ["FirstName1", "FirstName2"],
                "Entreprise": ["Company1", "Company2"],
                "Departement": ["Dept1", "Dept2"],
                "ManagerEmail": ["manager1@test.com", "manager2@test.com"],
                "Structure": ["Struct1", "Struct2"],
                "SSOMethod": ["AzureAD", "AzureAD"],
            }
        )

        self.df_n2f_users = pd.DataFrame(
            {
                "email": ["user1@test.com"],
                "firstName": ["FirstName1"],
                "lastName": ["User1"],
                "company": ["Company1"],
                "department": ["Dept1"],
                "managerEmail": ["manager1@test.com"],
                "structure": ["Struct1"],
                "ssoMethod": ["AzureAD"],
            }
        )

        self.df_n2f_companies = pd.DataFrame(
            {
                "id": ["comp1", "comp2"],
                "name": ["Company1", "Company2"],
            }
        )

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_create_only(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation - création uniquement."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Mock du synchronizer
        mock_sync_instance = Mock()
        mock_synchronizer_class.return_value = mock_sync_instance
        mock_sync_instance.create_entities.return_value = (
            self.df_agresso_users,
            "created",
        )

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_sync_instance.create_entities.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_update_only(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation - mise à jour uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = True
        self.mock_args.delete = False

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Mock du synchronizer
        mock_sync_instance = Mock()
        mock_synchronizer_class.return_value = mock_sync_instance
        mock_sync_instance.update_entities.return_value = (
            self.df_agresso_users,
            "updated",
        )

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_sync_instance.update_entities.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_delete_only(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation - suppression uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = True

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Mock du synchronizer
        mock_sync_instance = Mock()
        mock_synchronizer_class.return_value = mock_sync_instance
        mock_sync_instance.delete_entities.return_value = (
            self.df_agresso_users,
            "deleted",
        )

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_sync_instance.delete_entities.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_all_operations(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation - toutes les opérations."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Mock du synchronizer
        mock_sync_instance = Mock()
        mock_synchronizer_class.return_value = mock_sync_instance
        mock_sync_instance.create_entities.return_value = (
            self.df_agresso_users,
            "created",
        )
        mock_sync_instance.update_entities.return_value = (
            self.df_agresso_users,
            "updated",
        )
        mock_sync_instance.delete_entities.return_value = (
            self.df_agresso_users,
            "deleted",
        )

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_sync_instance.create_entities.assert_called_once()
        mock_sync_instance.update_entities.assert_called_once()
        mock_sync_instance.delete_entities.assert_called_once()
        self.assertEqual(len(result), 3)

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_with_filter(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation avec filtre."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Mock du synchronizer
        mock_sync_instance = Mock()
        mock_synchronizer_class.return_value = mock_sync_instance
        mock_sync_instance.create_entities.return_value = (
            self.df_agresso_users,
            "created",
        )

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction avec filtre
        result = user_process.synchronize(
            self.mock_context, "test_query.sql", "active_users"
        )

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_sync_instance.create_entities.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.user._load_agresso_users")
    @patch("business.process.user._load_n2f_data")
    @patch("business.process.user.UserSynchronizer")
    def test_synchronize_no_operations(
        self, mock_synchronizer_class, mock_load_n2f, mock_load_agresso
    ):
        """Test de synchronisation - aucune opération."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = (self.df_agresso_users, self.df_n2f_companies)
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        self.assertEqual(len(result), 0)

    @patch("business.process.user.select")
    @patch("business.process.user.normalize_agresso_users")
    def test_load_agresso_users(self, mock_normalize, mock_select):
        """Test du chargement des utilisateurs Agresso."""
        mock_select.return_value = self.df_agresso_users
        mock_normalize.return_value = self.df_agresso_users
        self.mock_context.get_config_value.return_value = {
            "sql-path": "path/to/sql",
            "prod": False,
        }

        result = user_process._load_agresso_users(self.mock_context, "test.sql")

        mock_select.assert_called_once()
        mock_normalize.assert_called_once()
        self.assertEqual(len(result), 2)

    @patch("n2f.client.N2fApiClient")
    @patch("business.process.user.normalize_n2f_users")
    @patch("business.process.user.build_n2f_mapping")
    def test_load_n2f_data(self, mock_build_mapping, mock_normalize, mock_n2f_client):
        """Test du chargement des données N2F."""
        mock_n2f_client.get_roles.return_value = pd.DataFrame()
        mock_n2f_client.get_userprofiles.return_value = pd.DataFrame()
        mock_n2f_client.get_companies.return_value = self.df_n2f_companies
        mock_n2f_client.get_users.return_value = self.df_n2f_users
        mock_normalize.return_value = self.df_n2f_users
        mock_build_mapping.return_value = {}

        df_users, df_companies = user_process._load_n2f_data(mock_n2f_client)

        self.assertEqual(mock_n2f_client.get_roles.call_count, 1)
        self.assertEqual(mock_n2f_client.get_userprofiles.call_count, 1)
        self.assertEqual(mock_n2f_client.get_companies.call_count, 1)
        self.assertEqual(mock_n2f_client.get_users.call_count, 1)
        self.assertEqual(len(df_users), 1)
        self.assertEqual(len(df_companies), 2)


if __name__ == "__main__":
    unittest.main()
