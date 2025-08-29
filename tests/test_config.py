"""
Tests unitaires pour les composants de configuration.
"""

import unittest
import sys
import os
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from core.config import SyncConfig, DatabaseConfig, ApiConfig, ScopeConfig, CacheConfig, ConfigLoader
from core.registry import SyncRegistry, RegistryEntry


class TestSyncConfig(unittest.TestCase):
    """Tests pour SyncConfig."""

    def test_sync_config_creation(self):
        """Test de création d'une configuration de synchronisation."""
        db_config = DatabaseConfig(host="localhost", port=1433, database="test_db")
        api_config = ApiConfig(base_urls="https://api.test.com", simulate=False)
        cache_config = CacheConfig(ttl=300, max_size=1000, enable_persistence=True)
        
        scopes = {
            "users": ScopeConfig(
                sql_filename="users.sql",
                sql_column_filter="active = 1",
                cache=cache_config
            )
        }
        
        config = SyncConfig(
            database=db_config,
            n2f=api_config,
            agresso={"sql-path": "/sql"},
            scopes=scopes
        )
        
        self.assertEqual(config.database.host, "localhost")
        self.assertEqual(config.n2f.base_urls, "https://api.test.com")
        self.assertEqual(config.agresso["sql-path"], "/sql")
        self.assertIn("users", config.scopes)

    def test_sync_config_defaults(self):
        """Test des valeurs par défaut de SyncConfig."""
        config = SyncConfig()
        
        self.assertIsNotNone(config.database)
        self.assertIsNotNone(config.n2f)
        self.assertIsNotNone(config.agresso)
        self.assertIsNotNone(config.scopes)

    def test_scope_config_creation(self):
        """Test de création d'une configuration de scope."""
        cache_config = CacheConfig(ttl=600, max_size=500)
        
        scope_config = ScopeConfig(
            sql_filename="test.sql",
            sql_column_filter="status = 'active'",
            cache=cache_config
        )
        
        self.assertEqual(scope_config.sql_filename, "test.sql")
        self.assertEqual(scope_config.sql_column_filter, "status = 'active'")
        self.assertEqual(scope_config.cache.ttl, 600)


class TestConfigLoader(unittest.TestCase):
    """Tests pour ConfigLoader."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.loader = ConfigLoader()

    def test_load_config_from_file(self):
        """Test de chargement de configuration depuis un fichier."""
        config_data = {
            "database": {
                "host": "test-host",
                "port": 1433,
                "database": "test_db"
            },
            "n2f": {
                "base_urls": "https://api.test.com",
                "simulate": True
            },
            "agresso": {
                "sql-path": "/test/sql"
            },
            "scopes": {
                "users": {
                    "sql_filename": "users.sql",
                    "sql_column_filter": "active = 1"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            config = self.loader.load_config(config_file)
            
            self.assertEqual(config.database.host, "test-host")
            self.assertEqual(config.n2f.base_urls, "https://api.test.com")
            self.assertEqual(config.n2f.simulate, True)
            self.assertEqual(config.agresso["sql-path"], "/test/sql")
            self.assertIn("users", config.scopes)
        finally:
            os.unlink(config_file)

    def test_load_config_invalid_file(self):
        """Test de chargement avec un fichier invalide."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_config("nonexistent.yaml")

    def test_load_config_invalid_yaml(self):
        """Test de chargement avec un YAML invalide."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            with self.assertRaises(Exception):
                self.loader.load_config(config_file)
        finally:
            os.unlink(config_file)

    def test_validate_config(self):
        """Test de validation de configuration."""
        # Configuration valide
        valid_config = SyncConfig()
        self.assertTrue(self.loader.validate_config(valid_config))
        
        # Configuration invalide (base_urls manquant)
        invalid_config = SyncConfig()
        invalid_config.n2f.base_urls = None
        with self.assertRaises(ValueError):
            self.loader.validate_config(invalid_config)


class TestSyncRegistry(unittest.TestCase):
    """Tests pour SyncRegistry."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.registry = SyncRegistry()

    def test_register_scope(self):
        """Test d'enregistrement d'un scope."""
        def test_sync_function(context, sql_filename):
            return "test_result"
        
        entry = RegistryEntry(
            name="test_scope",
            display_name="Test Scope",
            sync_function=test_sync_function,
            sql_filename="test.sql",
            sql_column_filter="active = 1"
        )
        
        self.registry.register(entry)
        
        # Vérifier que le scope est enregistré
        retrieved_entry = self.registry.get("test_scope")
        self.assertEqual(retrieved_entry.name, "test_scope")
        self.assertEqual(retrieved_entry.display_name, "Test Scope")
        self.assertEqual(retrieved_entry.sql_filename, "test.sql")
        self.assertEqual(retrieved_entry.sql_column_filter, "active = 1")

    def test_get_nonexistent_scope(self):
        """Test de récupération d'un scope inexistant."""
        with self.assertRaises(KeyError):
            self.registry.get("nonexistent_scope")

    def test_get_all_scopes(self):
        """Test de récupération de tous les scopes."""
        # Enregistrer plusieurs scopes
        def sync_func1(context, sql_filename):
            return "result1"
        
        def sync_func2(context, sql_filename):
            return "result2"
        
        entry1 = RegistryEntry("scope1", "Scope 1", sync_func1, "scope1.sql")
        entry2 = RegistryEntry("scope2", "Scope 2", sync_func2, "scope2.sql")
        
        self.registry.register(entry1)
        self.registry.register(entry2)
        
        all_scopes = self.registry.get_all_scopes()
        self.assertEqual(len(all_scopes), 2)
        self.assertIn("scope1", all_scopes)
        self.assertIn("scope2", all_scopes)

    def test_validate_registry(self):
        """Test de validation du registry."""
        # Registry vide est valide
        self.assertTrue(self.registry.validate())
        
        # Registry avec scope valide
        def valid_sync_function(context, sql_filename):
            return "valid_result"
        
        entry = RegistryEntry("valid_scope", "Valid Scope", valid_sync_function, "valid.sql")
        self.registry.register(entry)
        self.assertTrue(self.registry.validate())
        
        # Registry avec scope invalide (fonction manquante)
        invalid_entry = RegistryEntry("invalid_scope", "Invalid Scope", None, "invalid.sql")
        self.registry.register(invalid_entry)
        with self.assertRaises(ValueError):
            self.registry.validate()

    @patch('core.registry.inspect')
    def test_auto_discover_scopes(self, mock_inspect):
        """Test de découverte automatique des scopes."""
        # Mock du module pour simuler la découverte
        mock_module = Mock()
        mock_module.synchronize_test_scope = Mock()
        mock_module.other_function = Mock()
        
        # Configurer le mock pour simuler une fonction de synchronisation
        mock_inspect.isfunction.return_value = True
        mock_inspect.signature.return_value = Mock(parameters=['context', 'sql_filename'])
        
        # Simuler la découverte
        discovered_scopes = self.registry.auto_discover_scopes([mock_module])
        
        # Vérifier que la fonction synchronize_test_scope a été découverte
        self.assertIn("test_scope", discovered_scopes)
        self.assertEqual(discovered_scopes["test_scope"].name, "test_scope")

    def test_register_duplicate_scope(self):
        """Test d'enregistrement d'un scope en double."""
        def sync_function(context, sql_filename):
            return "result"
        
        entry1 = RegistryEntry("duplicate_scope", "Duplicate Scope", sync_function, "test1.sql")
        entry2 = RegistryEntry("duplicate_scope", "Duplicate Scope 2", sync_function, "test2.sql")
        
        # Premier enregistrement devrait réussir
        self.registry.register(entry1)
        
        # Deuxième enregistrement devrait échouer
        with self.assertRaises(ValueError):
            self.registry.register(entry2)


class TestRegistryEntry(unittest.TestCase):
    """Tests pour RegistryEntry."""

    def test_registry_entry_creation(self):
        """Test de création d'une entrée de registry."""
        def test_function(context, sql_filename):
            return "test"
        
        entry = RegistryEntry(
            name="test_scope",
            display_name="Test Scope",
            sync_function=test_function,
            sql_filename="test.sql",
            sql_column_filter="active = 1"
        )
        
        self.assertEqual(entry.name, "test_scope")
        self.assertEqual(entry.display_name, "Test Scope")
        self.assertEqual(entry.sync_function, test_function)
        self.assertEqual(entry.sql_filename, "test.sql")
        self.assertEqual(entry.sql_column_filter, "active = 1")

    def test_registry_entry_defaults(self):
        """Test des valeurs par défaut de RegistryEntry."""
        def test_function(context, sql_filename):
            return "test"
        
        entry = RegistryEntry(
            name="test_scope",
            display_name="Test Scope",
            sync_function=test_function,
            sql_filename="test.sql"
        )
        
        self.assertIsNone(entry.sql_column_filter)

    def test_registry_entry_str_representation(self):
        """Test de la représentation string de RegistryEntry."""
        def test_function(context, sql_filename):
            return "test"
        
        entry = RegistryEntry("test_scope", "Test Scope", test_function, "test.sql")
        
        str_repr = str(entry)
        self.assertIn("test_scope", str_repr)
        self.assertIn("Test Scope", str_repr)


if __name__ == '__main__':
    unittest.main()
