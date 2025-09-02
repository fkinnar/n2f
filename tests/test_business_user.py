#!/usr/bin/env python3
"""
Tests spécifiques pour le module business.process.user
"""

import unittest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import business.process.user as user_process
from core import SyncContext


class TestBusinessUser(unittest.TestCase):
    """Tests pour le module business.process.user."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Mock du contexte
        self.mock_context = Mock(spec=SyncContext)
        self.mock_context.base_dir = "/test/base/dir"
        self.mock_context.db_user = "test_user"
        self.mock_context.db_password = "test_password"
        self.mock_context.client_id = "test_client_id"
        self.mock_context.client_secret = "test_client_secret"
        self.mock_context.tenant_id = "test_tenant_id"
        self.mock_context.scope = "test_scope"

        # Mock des arguments
        self.mock_args = Mock()
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True
        self.mock_context.args = self.mock_args

        # Mock de la configuration
        self.mock_agresso_config = Mock()
        self.mock_agresso_config.sql_path = "sql"
        self.mock_agresso_config.prod = False

        self.mock_n2f_config = Mock()
        self.mock_n2f_config.sandbox = False

        # Mock du client N2F
        self.mock_n2f_client = Mock()

        # DataFrames de test
        self.df_agresso_users = pd.DataFrame({
            'email': ['user1@test.com', 'user2@test.com'],
            'firstname': ['John', 'Jane'],
            'lastname': ['Doe', 'Smith']
        })

        self.df_n2f_users = pd.DataFrame({
            'email': ['existing@test.com'],
            'firstname': ['Existing'],
            'lastname': ['User']
        })

        self.df_n2f_companies = pd.DataFrame({
            'uuid': ['uuid1', 'uuid2'],
            'name': ['Company 1', 'Company 2']
        })

        self.df_roles = pd.DataFrame({
            'id': ['role1', 'role2'],
            'name': ['Role 1', 'Role 2']
        })

        self.df_userprofiles = pd.DataFrame({
            'id': ['profile1', 'profile2'],
            'name': ['Profile 1', 'Profile 2']
        })

    @patch('business.process.user.normalize_agresso_users')
    @patch('business.process.user.select')
    def test_load_agresso_users_success(self, mock_select, mock_normalize):
        """Test de chargement des utilisateurs Agresso avec succès."""
        # Configuration des mocks
        mock_select.return_value = self.df_agresso_users
        mock_normalize.return_value = self.df_agresso_users
        self.mock_context.get_config_value.side_effect = lambda key: self.mock_agresso_config if key == "agresso" else self.mock_n2f_config

        # Exécution de la fonction
        result = user_process._load_agresso_users(self.mock_context, "test_query.sql")

        # Vérifications
        mock_select.assert_called_once()
        mock_normalize.assert_called_once_with(self.df_agresso_users)
        self.assertEqual(len(result), 2)

    @patch('business.process.user.normalize_agresso_users')
    @patch('business.process.user.select')
    def test_load_agresso_users_empty_result(self, mock_select, mock_normalize):
        """Test de chargement des utilisateurs Agresso avec résultat vide."""
        # Configuration des mocks
        empty_df = pd.DataFrame()
        mock_select.return_value = empty_df
        mock_normalize.return_value = empty_df
        self.mock_context.get_config_value.side_effect = lambda key: self.mock_agresso_config if key == "agresso" else self.mock_n2f_config

        # Exécution de la fonction
        result = user_process._load_agresso_users(self.mock_context, "test_query.sql")

        # Vérifications
        self.assertTrue(result.empty)

    @patch('business.process.user.normalize_n2f_users')
    @patch('business.process.user.build_n2f_mapping')
    def test_load_n2f_data_success(self, mock_build_mapping, mock_normalize):
        """Test de chargement des données N2F avec succès."""
        # Configuration des mocks
        mock_build_mapping.side_effect = [{'profile1': 'Profile 1'}, {'role1': 'Role 1'}]
        mock_normalize.return_value = self.df_n2f_users

        self.mock_n2f_client.get_roles.return_value = self.df_roles
        self.mock_n2f_client.get_userprofiles.return_value = self.df_userprofiles
        self.mock_n2f_client.get_companies.return_value = self.df_n2f_companies
        self.mock_n2f_client.get_users.return_value = self.df_n2f_users

        # Exécution de la fonction
        result_users, result_companies = user_process._load_n2f_data(self.mock_n2f_client)

        # Vérifications
        self.mock_n2f_client.get_roles.assert_called_once()
        self.mock_n2f_client.get_userprofiles.assert_called_once()
        self.mock_n2f_client.get_companies.assert_called_once()
        self.mock_n2f_client.get_users.assert_called_once()
        mock_build_mapping.assert_called()
        mock_normalize.assert_called_once()
        self.assertEqual(len(result_users), 1)
        self.assertEqual(len(result_companies), 2)

    @patch('business.process.user.normalize_n2f_users')
    @patch('business.process.user.build_n2f_mapping')
    def test_load_n2f_data_empty_results(self, mock_build_mapping, mock_normalize):
        """Test de chargement des données N2F avec résultats vides."""
        # Configuration des mocks
        empty_df = pd.DataFrame()
        mock_build_mapping.side_effect = [{}, {}]
        mock_normalize.return_value = empty_df

        self.mock_n2f_client.get_roles.return_value = empty_df
        self.mock_n2f_client.get_userprofiles.return_value = empty_df
        self.mock_n2f_client.get_companies.return_value = empty_df
        self.mock_n2f_client.get_users.return_value = empty_df

        # Exécution de la fonction
        result_users, result_companies = user_process._load_n2f_data(self.mock_n2f_client)

        # Vérifications
        self.assertTrue(result_users.empty)
        self.assertTrue(result_companies.empty)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_create_only(self, mock_reporting, mock_synchronizer_class,
                                   mock_load_agresso, mock_load_n2f):
        """Test de synchronisation - création uniquement."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.create_entities.return_value = (self.df_agresso_users, "created")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        mock_load_n2f.assert_called_once()
        mock_synchronizer_class.assert_called_once()
        mock_synchronizer.create_entities.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_update_only(self, mock_reporting, mock_synchronizer_class,
                                   mock_load_agresso, mock_load_n2f):
        """Test de synchronisation - mise à jour uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = True
        self.mock_args.delete = False

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.update_entities.return_value = (self.df_agresso_users, "updated")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronizer.update_entities.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_delete_only(self, mock_reporting, mock_synchronizer_class,
                                   mock_load_agresso, mock_load_n2f):
        """Test de synchronisation - suppression uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = True

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.delete_entities.return_value = (self.df_agresso_users, "deleted")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronizer.delete_entities.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_all_operations(self, mock_reporting, mock_synchronizer_class,
                                      mock_load_agresso, mock_load_n2f):
        """Test de synchronisation - toutes les opérations."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.create_entities.return_value = (self.df_agresso_users, "created")
        mock_synchronizer.update_entities.return_value = (self.df_agresso_users, "updated")
        mock_synchronizer.delete_entities.return_value = (self.df_agresso_users, "deleted")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronizer.create_entities.assert_called_once()
        mock_synchronizer.update_entities.assert_called_once()
        mock_synchronizer.delete_entities.assert_called_once()
        self.assertEqual(mock_reporting.call_count, 3)
        self.assertEqual(len(result), 3)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_empty_results(self, mock_reporting, mock_synchronizer_class,
                                     mock_load_agresso, mock_load_n2f):
        """Test de synchronisation avec résultats vides."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.create_entities.return_value = (pd.DataFrame(), "created")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronizer.create_entities.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 0)  # Aucun résultat ajouté car DataFrame vide

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_with_sql_column_filter(self, mock_reporting, mock_synchronizer_class,
                                              mock_load_agresso, mock_load_n2f):
        """Test de synchronisation avec filtre de colonne SQL."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer
        mock_synchronizer.create_entities.return_value = (self.df_agresso_users, "created")

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction avec filtre
        result = user_process.synchronize(self.mock_context, "test_query.sql", "active_users")

        # Vérifications
        mock_load_agresso.assert_called_once_with(self.mock_context, "test_query.sql")
        # Le filtre sql_column_filter n'est pas utilisé dans la fonction actuelle
        self.assertEqual(len(result), 1)

    @patch('business.process.user._load_n2f_data')
    @patch('business.process.user._load_agresso_users')
    @patch('business.process.user.UserSynchronizer')
    @patch('business.process.user.reporting')
    def test_synchronize_no_operations(self, mock_reporting, mock_synchronizer_class,
                                     mock_load_agresso, mock_load_n2f):
        """Test de synchronisation sans opérations."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_load_agresso.return_value = self.df_agresso_users
        mock_load_n2f.return_value = (self.df_n2f_users, self.df_n2f_companies)

        mock_synchronizer = Mock()
        mock_synchronizer_class.return_value = mock_synchronizer

        self.mock_context.get_config_value.side_effect = lambda key: self.mock_n2f_config if key == "n2f" else self.mock_agresso_config

        # Exécution de la fonction
        result = user_process.synchronize(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronizer.create_entities.assert_not_called()
        mock_synchronizer.update_entities.assert_not_called()
        mock_synchronizer.delete_entities.assert_not_called()
        mock_reporting.assert_not_called()
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
