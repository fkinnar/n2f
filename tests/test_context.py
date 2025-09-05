"""
Tests unitaires pour le module de contexte.

Ce module teste les fonctionnalités du contexte de synchronisation :
- Création du contexte
- Récupération des valeurs de configuration
- Compatibilité avec les anciens et nouveaux formats
"""

from unittest.mock import Mock

import agresso.database as agresso_db
from core import SyncContext

import unittest
import argparse

from pathlib import Path
from typing import Dict, Any

# Ajout du chemin du projet pour les imports
from core.config import SyncConfig, DatabaseConfig, ApiConfig


class TestSyncContext(unittest.TestCase):
    """Tests pour la classe SyncContext."""

    def setUp(self) -> None:
        """Configuration initiale pour les tests."""
        self.args: Mock = Mock(spec=argparse.Namespace)
        self.base_dir: Path = Path("/test / base/dir")
        self.db_user: str = "test_user"
        self.db_password: str = "test_password"
        self.client_id: str = "test_client_id"
        self.client_secret: str = "test_client_secret"

    def test_initialization_with_dict_config(self) -> None:
        """Test de l'initialisation avec une configuration en format dict."""
        config: Dict[str, Any] = {
            "agresso": {"host": "localhost", "port": 5432},
            "n2f": {"base_url": "https://api.n2f.com", "timeout": 30},
            "cache": {"enabled": True, "ttl": 3600},
        }

        context: SyncContext = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.assertEqual(context.args, self.args)
        self.assertEqual(context.config, config)
        self.assertEqual(context.base_dir, self.base_dir)
        self.assertEqual(context.db_user, self.db_user)
        self.assertEqual(context.db_password, self.db_password)
        self.assertEqual(context.client_id, self.client_id)
        self.assertEqual(context.client_secret, self.client_secret)

    def test_initialization_with_syncconfig(self) -> None:
        """Test de l'initialisation avec une configuration SyncConfig."""
        # Créer une configuration SyncConfig
        database_config: DatabaseConfig = DatabaseConfig(
            prod=True,
            sql_path="test_sql",
            sql_filename_users="test_users.sql",
            sql_filename_customaxes="test_axes.sql",
        )
        api_config: ApiConfig = ApiConfig(
            base_urls="https://api.n2f.com / services/api / v2/",
            sandbox=True,
            simulate=False,
        )
        config: SyncConfig = SyncConfig(
            database=database_config, api=api_config, scopes={}, cache=Mock()
        )

        context: SyncContext = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.assertEqual(context.args, self.args)
        self.assertEqual(context.config, config)
        self.assertEqual(context.base_dir, self.base_dir)
        self.assertEqual(context.db_user, self.db_user)
        self.assertEqual(context.db_password, self.db_password)
        self.assertEqual(context.client_id, self.client_id)
        self.assertEqual(context.client_secret, self.client_secret)

    def test_get_config_value_dict_format_existing_key(self):
        """Test de récupération d'une valeur existante avec format dict."""
        config = {
            "agresso": {"host": "localhost", "port": 5432},
            "n2f": {"base_url": "https://api.n2f.com"},
            "cache": {"enabled": True},
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test récupération de clés existantes
        self.assertEqual(
            context.get_config_value("agresso"), {"host": "localhost", "port": 5432}
        )
        self.assertEqual(
            context.get_config_value("n2f"), {"base_url": "https://api.n2f.com"}
        )
        self.assertEqual(context.get_config_value("cache"), {"enabled": True})

    def test_get_config_value_dict_format_missing_key(self):
        """Test de récupération d'une valeur manquante avec format dict."""
        config = {
            "agresso": {"host": "localhost"},
            "n2f": {"base_url": "https://api.n2f.com"},
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test récupération de clés manquantes
        self.assertIsNone(context.get_config_value("missing_key"))
        self.assertEqual(context.get_config_value("missing_key", "default"), "default")
        self.assertEqual(
            context.get_config_value("cache", {"enabled": False}), {"enabled": False}
        )

    def test_get_config_value_syncconfig_format_existing_key(self):
        """Test de récupération d'une valeur existante avec format SyncConfig."""
        # Créer une configuration SyncConfig
        database_config = DatabaseConfig(
            prod=True,
            sql_path="test_sql",
            sql_filename_users="test_users.sql",
            sql_filename_customaxes="test_axes.sql",
        )
        api_config = ApiConfig(
            base_urls="https://api.n2f.com / services/api / v2/",
            sandbox=True,
            simulate=False,
        )
        config = SyncConfig(
            database=database_config, api=api_config, scopes={}, cache=Mock()
        )

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test récupération des clés spéciales
        self.assertEqual(context.get_config_value("agresso"), database_config)
        self.assertEqual(context.get_config_value("n2f"), api_config)

        # Test récupération d'attributs existants
        self.assertEqual(context.get_config_value("database"), database_config)
        self.assertEqual(context.get_config_value("api"), api_config)

    def test_get_config_value_syncconfig_format_missing_key(self):
        """Test de récupération d'une valeur manquante avec format SyncConfig."""
        # Créer une configuration SyncConfig
        database_config = DatabaseConfig(
            prod=True,
            sql_path="test_sql",
            sql_filename_users="test_users.sql",
            sql_filename_customaxes="test_axes.sql",
        )
        api_config = ApiConfig(
            base_urls="https://api.n2f.com / services/api / v2/",
            sandbox=True,
            simulate=False,
        )
        config = SyncConfig(
            database=database_config, api=api_config, scopes={}, cache=Mock()
        )

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test récupération de clés manquantes
        self.assertIsNone(context.get_config_value("missing_key"))
        self.assertEqual(context.get_config_value("missing_key", "default"), "default")
        self.assertEqual(
            context.get_config_value("nonexistent", {"test": "value"}),
            {"test": "value"},
        )

    def test_get_config_value_syncconfig_format_with_default(self):
        """Test de récupération avec valeur par défaut avec format SyncConfig."""
        # Créer une configuration SyncConfig
        database_config = DatabaseConfig(
            prod=True,
            sql_path="test_sql",
            sql_filename_users="test_users.sql",
            sql_filename_customaxes="test_axes.sql",
        )
        api_config = ApiConfig(
            base_urls="https://api.n2f.com / services/api / v2/",
            sandbox=True,
            simulate=False,
        )
        config = SyncConfig(
            database=database_config, api=api_config, scopes={}, cache=Mock()
        )

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test avec valeurs par défaut pour une clé qui n'existe pas
        default_value = {"enabled": False, "ttl": 1800}
        result = context.get_config_value("nonexistent_key", default_value)
        self.assertEqual(result, default_value)

        # Test que la clé "cache" retourne bien le Mock (car elle existe dans
        # SyncConfig)
        cache_result = context.get_config_value("cache")
        self.assertIsInstance(cache_result, Mock)

    def test_get_config_value_edge_cases(self):
        """Test de cas limites pour get_config_value."""
        config = {
            "empty_string": "",
            "zero": 0,
            "false": False,
            "none": None,
            "empty_dict": {},
            "empty_list": [],
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test que les valeurs "falsy" sont correctement retournées
        self.assertEqual(context.get_config_value("empty_string"), "")
        self.assertEqual(context.get_config_value("zero"), 0)
        self.assertEqual(context.get_config_value("false"), False)
        self.assertIsNone(context.get_config_value("none"))
        self.assertEqual(context.get_config_value("empty_dict"), {})
        self.assertEqual(context.get_config_value("empty_list"), [])

    def test_get_config_value_nested_access(self):
        """Test d'accès aux valeurs imbriquées."""
        config = {
            "agresso": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "db_user", "password": "db_pass"},
                }
            },
            "n2f": {
                "api": {
                    "base_url": "https://api.n2f.com",
                    "endpoints": {"users": "/users", "projects": "/projects"},
                }
            },
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test récupération de valeurs imbriquées
        self.assertEqual(context.get_config_value("agresso"), config["agresso"])
        self.assertEqual(context.get_config_value("n2f"), config["n2f"])

        # Test que les valeurs imbriquées ne sont pas accessibles directement
        self.assertIsNone(context.get_config_value("agresso.database"))
        self.assertIsNone(context.get_config_value("n2f.api"))

    def test_context_immutability(self):
        """Test que le contexte est bien configuré après création."""
        config = {
            "agresso": {"host": "localhost"},
            "n2f": {"base_url": "https://api.n2f.com"},
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Vérifier que les attributs sont bien définis
        self.assertIsNotNone(context.args)
        self.assertIsNotNone(context.config)
        self.assertIsNotNone(context.base_dir)
        self.assertIsNotNone(context.db_user)
        self.assertIsNotNone(context.db_password)
        self.assertIsNotNone(context.client_id)
        self.assertIsNotNone(context.client_secret)

        # Vérifier que les attributs peuvent être modifiés (dataclass mutable par
        # défaut)
        # Ce test vérifie que la classe fonctionne correctement
        original_args = context.args
        context.args = Mock(spec=argparse.Namespace)
        self.assertNotEqual(context.args, original_args)

    def test_context_with_none_values(self):
        """Test de création du contexte avec des valeurs None."""
        context = SyncContext(
            args=self.args,
            config={},
            base_dir=self.base_dir,
            db_user=None,
            db_password=None,
            client_id=None,
            client_secret=None,
        )

        self.assertIsNone(context.db_user)
        self.assertIsNone(context.db_password)
        self.assertIsNone(context.client_id)
        self.assertIsNone(context.client_secret)

    def test_context_with_empty_config(self):
        """Test de création du contexte avec une configuration vide."""
        context = SyncContext(
            args=self.args,
            config={},
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test que get_config_value fonctionne avec une config vide
        self.assertIsNone(context.get_config_value("any_key"))
        self.assertEqual(context.get_config_value("any_key", "default"), "default")

    def test_context_repr_and_str(self):
        """Test de la représentation du contexte."""
        config = {
            "agresso": {"host": "localhost"},
            "n2f": {"base_url": "https://api.n2f.com"},
        }

        context = SyncContext(
            args=self.args,
            config=config,
            base_dir=self.base_dir,
            db_user=self.db_user,
            db_password=self.db_password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Test que le contexte peut être converti en string
        context_str = str(context)
        self.assertIsInstance(context_str, str)
        self.assertIn("SyncContext", context_str)

        # Test que le contexte a une représentation
        context_repr = repr(context)
        self.assertIsInstance(context_repr, str)
        self.assertIn("SyncContext", context_repr)


if __name__ == "__main__":
    unittest.main()
