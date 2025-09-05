"""
Tests unitaires pour le module de base de données Agresso.

Ce module teste les fonctionnalités d'accès à la base de données
Agresso et la récupération des données.
"""

import pandas as pd

import unittest

from unittest.mock import Mock, patch
import agresso.database as database_module


class TestExecuteQuery(unittest.TestCase):
    """Tests pour la fonction execute_query."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Mock de la connexion IrisConnect
        self.mock_db = Mock()
        self.mock_sqlalchemy_engine = Mock()
        self.mock_db.sqlalchemy = self.mock_sqlalchemy_engine

        # Requêtes de test
        self.simple_query = "SELECT * FROM users"
        self.complex_query = """
            SELECT u.id, u.name, c.company_name
            FROM users u
            LEFT JOIN companies c ON u.company_id = c.id
            WHERE u.active = 1
        """

        # DataFrames de résultat de test
        self.df_users = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "email": ["alice@test.com", "bob@test.com", "charlie@test.com"],
            }
        )

        self.df_empty = pd.DataFrame()

        self.df_single_row = pd.DataFrame({"count": [42]})

    @patch("pandas.read_sql_query")
    def test_execute_query_success(self, mock_read_sql):
        """Test d'exécution réussie d'une requête simple."""
        # Configuration du mock
        mock_read_sql.return_value = self.df_users

        # Exécution de la fonction
        result = database_module.execute_query(self.mock_db, self.simple_query)

        # Vérifications
        mock_read_sql.assert_called_once_with(
            self.simple_query, self.mock_sqlalchemy_engine
        )
        pd.testing.assert_frame_equal(result, self.df_users)

    @patch("pandas.read_sql_query")
    def test_execute_query_complex(self, mock_read_sql):
        """Test d'exécution d'une requête complexe."""
        mock_read_sql.return_value = self.df_users

        result = database_module.execute_query(self.mock_db, self.complex_query)

        mock_read_sql.assert_called_once_with(
            self.complex_query, self.mock_sqlalchemy_engine
        )
        pd.testing.assert_frame_equal(result, self.df_users)

    @patch("pandas.read_sql_query")
    def test_execute_query_empty_result(self, mock_read_sql):
        """Test d'exécution d'une requête retournant un résultat vide."""
        mock_read_sql.return_value = self.df_empty

        result = database_module.execute_query(
            self.mock_db, "SELECT * FROM users WHERE id = -1"
        )

        mock_read_sql.assert_called_once()
        pd.testing.assert_frame_equal(result, self.df_empty)

    @patch("pandas.read_sql_query")
    def test_execute_query_single_row(self, mock_read_sql):
        """Test d'exécution d'une requête retournant une seule ligne."""
        mock_read_sql.return_value = self.df_single_row

        result = database_module.execute_query(
            self.mock_db, "SELECT COUNT(*) as count FROM users"
        )

        mock_read_sql.assert_called_once()
        pd.testing.assert_frame_equal(result, self.df_single_row)

    @patch("pandas.read_sql_query")
    def test_execute_query_with_parameters(self, mock_read_sql):
        """Test d'exécution d'une requête avec des paramètres (chaîne)."""
        mock_read_sql.return_value = self.df_users

        parameterized_query = "SELECT * FROM users WHERE name = 'Alice'"
        result = database_module.execute_query(self.mock_db, parameterized_query)

        mock_read_sql.assert_called_once_with(
            parameterized_query, self.mock_sqlalchemy_engine
        )
        pd.testing.assert_frame_equal(result, self.df_users)

    @patch("pandas.read_sql_query")
    def test_execute_query_different_databases(self, mock_read_sql):
        """Test d'exécution avec différentes connexions de base de données."""
        mock_read_sql.return_value = self.df_users

        # Créer différentes connexions mock
        db1 = Mock()
        db1.sqlalchemy = Mock()

        db2 = Mock()
        db2.sqlalchemy = Mock()

        # Exécuter sur la première base
        result1 = database_module.execute_query(db1, self.simple_query)

        # Exécuter sur la deuxième base
        result2 = database_module.execute_query(db2, self.simple_query)

        # Vérifier que les bonnes connexions ont été utilisées
        calls = mock_read_sql.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0][1], db1.sqlalchemy)
        self.assertEqual(calls[1][0][1], db2.sqlalchemy)

    @patch("pandas.read_sql_query")
    def test_execute_query_sql_error(self, mock_read_sql):
        """Test de gestion d'erreur SQL."""
        # Simuler une erreur SQL
        mock_read_sql.side_effect = Exception("SQL syntax error")

        with self.assertRaises(Exception) as context:
            database_module.execute_query(
                self.mock_db, "SELECT * FROM nonexistent_table"
            )

        self.assertIn("SQL syntax error", str(context.exception))

    @patch("pandas.read_sql_query")
    def test_execute_query_connection_error(self, mock_read_sql):
        """Test de gestion d'erreur de connexion."""
        # Simuler une erreur de connexion
        mock_read_sql.side_effect = Exception("Connection refused")

        with self.assertRaises(Exception) as context:
            database_module.execute_query(self.mock_db, self.simple_query)

        self.assertIn("Connection refused", str(context.exception))

    @patch("pandas.read_sql_query")
    def test_execute_query_various_data_types(self, mock_read_sql):
        """Test avec différents types de données dans le résultat."""
        # DataFrame avec différents types de données
        mixed_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "salary": [50000.0, 60000.5, 70000.25],
                "active": [True, False, True],
                "hire_date": pd.to_datetime(["2020-01-01", "2021-01-01", "2022-01-01"]),
                "notes": ["Good", None, "Excellent"],
            }
        )

        mock_read_sql.return_value = mixed_df

        result = database_module.execute_query(self.mock_db, "SELECT * FROM employees")

        pd.testing.assert_frame_equal(result, mixed_df)

    @patch("pandas.read_sql_query")
    def test_execute_query_large_result(self, mock_read_sql):
        """Test avec un grand jeu de résultats."""
        # Simuler un grand DataFrame
        large_df = pd.DataFrame(
            {"id": range(1000), "value": [f"value_{i}" for i in range(1000)]}
        )

        mock_read_sql.return_value = large_df

        result = database_module.execute_query(
            self.mock_db, "SELECT * FROM large_table"
        )

        mock_read_sql.assert_called_once()
        self.assertEqual(len(result), 1000)
        pd.testing.assert_frame_equal(result, large_df)

    def test_execute_query_db_connection_object(self):
        """Test que la fonction utilise bien l'attribut sqlalchemy de l'objet db."""
        with patch("pandas.read_sql_query") as mock_read_sql:
            mock_read_sql.return_value = self.df_empty

            # Créer un mock avec un attribut sqlalchemy spécifique
            specific_engine = Mock()
            db_with_engine = Mock()
            db_with_engine.sqlalchemy = specific_engine

            database_module.execute_query(db_with_engine, "SELECT 1")

            # Vérifier que c'est bien l'engine spécifique qui a été utilisé
            mock_read_sql.assert_called_once_with("SELECT 1", specific_engine)

    @patch("pandas.read_sql_query")
    def test_execute_query_whitespace_query(self, mock_read_sql):
        """Test avec une requête contenant des espaces/retours à la ligne."""
        mock_read_sql.return_value = self.df_users

        whitespace_query = """

            SELECT *
            FROM users
            WHERE active = 1

        """

        result = database_module.execute_query(self.mock_db, whitespace_query)

        # Vérifier que la requête est passée telle quelle (avec les espaces)
        mock_read_sql.assert_called_once_with(
            whitespace_query, self.mock_sqlalchemy_engine
        )
        pd.testing.assert_frame_equal(result, self.df_users)

    @patch("pandas.read_sql_query")
    def test_execute_query_special_characters(self, mock_read_sql):
        """Test avec une requête contenant des caractères spéciaux."""
        mock_read_sql.return_value = self.df_users

        special_query = "SELECT * FROM users WHERE name LIKE '%été%' AND notes = 'café'"

        result = database_module.execute_query(self.mock_db, special_query)

        mock_read_sql.assert_called_once_with(
            special_query, self.mock_sqlalchemy_engine
        )
        pd.testing.assert_frame_equal(result, self.df_users)


if __name__ == "__main__":
    unittest.main()
