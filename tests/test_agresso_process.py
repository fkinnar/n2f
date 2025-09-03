#!/usr/bin/env python3
"""
Tests pour le module agresso.process
"""

import unittest
import sys
import os
import tempfile
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, mock_open

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

import agresso.process as agresso_process


class TestAgressoProcess(unittest.TestCase):
    """Tests pour le module agresso.process."""

    def setUp(self) -> None:
        """Configuration initiale pour les tests."""
        # Données de test
        self.test_df: pd.DataFrame = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "email": ["alice@test.com", "bob@test.com", "charlie@test.com"],
            }
        )

        # Paramètres de test
        self.base_dir = "/test/base/dir"
        self.db_user = "test_user"
        self.db_password = "test_password"
        self.sql_path = "sql"
        self.sql_filename = "test_query.sql"
        self.test_query = "SELECT * FROM users WHERE active = 1"

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_with_cache_hit(
        self,
        mock_file: Mock,
        mock_iris_connect: Mock,
        mock_execute_query: Mock,
        mock_set_cache: Mock,
        mock_get_cache: Mock,
    ) -> None:
        """Test de la fonction select avec un hit de cache."""
        # Configuration des mocks
        mock_get_cache.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications
        mock_get_cache.assert_called_once()
        mock_file.assert_called_once()
        mock_iris_connect.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_set_cache.assert_not_called()
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_with_cache_miss(
        self,
        mock_file: Mock,
        mock_iris_connect: Mock,
        mock_execute_query: Mock,
        mock_set_cache: Mock,
        mock_get_cache: Mock,
    ) -> None:
        """Test de la fonction select avec un miss de cache."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications
        mock_get_cache.assert_called_once()
        mock_file.assert_called_once()
        mock_iris_connect.assert_called_once()
        mock_execute_query.assert_called_once_with(
            mock_iris_instance, "SELECT * FROM users"
        )
        mock_set_cache.assert_called_once()
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_without_cache(
        self,
        mock_file: Mock,
        mock_iris_connect: Mock,
        mock_execute_query: Mock,
        mock_set_cache: Mock,
        mock_get_cache: Mock,
    ) -> None:
        """Test de la fonction select sans cache."""
        # Configuration des mocks
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=False,
        )

        # Vérifications
        mock_get_cache.assert_not_called()
        mock_file.assert_called_once()
        mock_iris_connect.assert_called_once()
        mock_execute_query.assert_called_once_with(
            mock_iris_instance, "SELECT * FROM users"
        )
        mock_set_cache.assert_not_called()
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_production_mode(
        self,
        mock_file: Mock,
        mock_iris_connect: Mock,
        mock_execute_query: Mock,
        mock_set_cache: Mock,
        mock_get_cache: Mock,
    ) -> None:
        """Test de la fonction select en mode production."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=True,
            cache=True,
        )

        # Vérifications
        mock_iris_connect.assert_called_once_with(
            server=mock_iris_connect.Server.Production,
            database=mock_iris_connect.Database.AgrProd,
            odbc_trust=False,
            user=self.db_user,
            password=self.db_password,
        )
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_development_mode(
        self,
        mock_file,
        mock_iris_connect,
        mock_execute_query,
        mock_set_cache,
        mock_get_cache,
    ):
        """Test de la fonction select en mode développement."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications
        mock_iris_connect.assert_called_once_with(
            server=mock_iris_connect.Server.Development,
            database=mock_iris_connect.Database.AgrDev,
            odbc_trust=False,
            user=self.db_user,
            password=self.db_password,
        )
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_complex_query(
        self,
        mock_file,
        mock_iris_connect,
        mock_execute_query,
        mock_set_cache,
        mock_get_cache,
    ):
        """Test de la fonction select avec une requête complexe."""
        complex_query = """
        SELECT u.id, u.name, c.company_name
        FROM users u
        LEFT JOIN companies c ON u.company_id = c.id
        WHERE u.active = 1
        ORDER BY u.name
        """

        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Mock du fichier avec une requête complexe
        mock_file.return_value.read.return_value = complex_query

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications
        mock_execute_query.assert_called_once_with(mock_iris_instance, complex_query)
        pd.testing.assert_frame_equal(result, self.test_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    def test_select_file_not_found(
        self, mock_iris_connect, mock_execute_query, mock_set_cache, mock_get_cache
    ):
        """Test de la fonction select avec un fichier SQL inexistant."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Test avec un fichier inexistant
        with self.assertRaises(FileNotFoundError):
            agresso_process.select(
                base_dir="/invalid/path",
                db_user=self.db_user,
                db_password=self.db_password,
                sql_path="sql",
                sql_filename="nonexistent.sql",
                prod=False,
                cache=True,
            )

        # Vérifications
        mock_iris_connect.assert_not_called()
        mock_execute_query.assert_not_called()

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_empty_result(
        self,
        mock_file,
        mock_iris_connect,
        mock_execute_query,
        mock_set_cache,
        mock_get_cache,
    ):
        """Test de la fonction select avec un résultat vide."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        empty_df = pd.DataFrame()
        mock_execute_query.return_value = empty_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        result = agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications
        mock_execute_query.assert_called_once()
        mock_set_cache.assert_called_once()
        pd.testing.assert_frame_equal(result, empty_df)

    @patch("agresso.process.get_from_cache")
    @patch("agresso.process.set_in_cache")
    @patch("agresso.process.execute_query")
    @patch("agresso.process.IrisConnect")
    @patch("builtins.open", new_callable=mock_open, read_data="SELECT * FROM users")
    def test_select_cache_parameters(
        self,
        mock_file,
        mock_iris_connect,
        mock_execute_query,
        mock_set_cache,
        mock_get_cache,
    ):
        """Test des paramètres de cache utilisés."""
        # Configuration des mocks
        mock_get_cache.return_value = None
        mock_execute_query.return_value = self.test_df
        mock_iris_instance = Mock()
        mock_iris_connect.return_value = mock_iris_instance

        # Exécution de la fonction
        agresso_process.select(
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            sql_path=self.sql_path,
            sql_filename=self.sql_filename,
            prod=False,
            cache=True,
        )

        # Vérifications des paramètres de cache
        expected_sql_file = os.path.join(
            self.base_dir, "..", self.sql_path, self.sql_filename
        )
        mock_get_cache.assert_called_once_with(
            "agresso_select",
            expected_sql_file,
            False,
            self.db_user,
            "SELECT * FROM users",
        )
        mock_set_cache.assert_called_once_with(
            self.test_df,
            "agresso_select",
            expected_sql_file,
            False,
            self.db_user,
            "SELECT * FROM users",
        )


if __name__ == "__main__":
    unittest.main()
