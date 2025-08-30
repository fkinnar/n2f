import unittest
import sys
import os

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import pandas as pd
from unittest.mock import Mock, patch
import helper.cache as cache_module


class TestCacheSimple(unittest.TestCase):
    """Tests pour le module de cache simple helper/cache.py."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Nettoyer le cache avant chaque test
        cache_module.clear_cache()

        # Créer des DataFrames de test
        self.df1 = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
        self.df2 = pd.DataFrame({'id': [3, 4], 'name': ['Charlie', 'David']})
        self.df_empty = pd.DataFrame()

    def tearDown(self):
        """Nettoyage après chaque test."""
        cache_module.clear_cache()

    def test_make_cache_key_simple(self):
        """Test de création de clé de cache simple."""
        key = cache_module.make_cache_key("get_users")

        expected = ("get_users", ())
        self.assertEqual(key, expected)

    def test_make_cache_key_with_parameters(self):
        """Test de création de clé de cache avec paramètres."""
        key = cache_module.make_cache_key("get_users", "scope1", 100, True)

        expected = ("get_users", ("scope1", 100, True))
        self.assertEqual(key, expected)

    def test_make_cache_key_with_mixed_types(self):
        """Test de création de clé de cache avec types mixtes."""
        key = cache_module.make_cache_key("get_data", "string", 42, True, None, [1, 2, 3])

        expected = ("get_data", ("string", 42, True, None, [1, 2, 3]))
        self.assertEqual(key, expected)

    def test_make_cache_key_different_functions(self):
        """Test que différentes fonctions génèrent des clés différentes."""
        key1 = cache_module.make_cache_key("get_users")
        key2 = cache_module.make_cache_key("get_companies")

        self.assertNotEqual(key1, key2)

    def test_make_cache_key_different_parameters(self):
        """Test que différents paramètres génèrent des clés différentes."""
        key1 = cache_module.make_cache_key("get_users", "scope1")
        key2 = cache_module.make_cache_key("get_users", "scope2")

        self.assertNotEqual(key1, key2)

    def test_get_from_cache_empty_cache(self):
        """Test de récupération depuis un cache vide."""
        result = cache_module.get_from_cache("get_users")

        self.assertIsNone(result)

    def test_get_from_cache_with_parameters_empty(self):
        """Test de récupération avec paramètres depuis un cache vide."""
        result = cache_module.get_from_cache("get_users", "scope1", 100)

        self.assertIsNone(result)

    def test_set_in_cache_and_get(self):
        """Test de stockage et récupération depuis le cache."""
        # Stocker dans le cache
        cache_module.set_in_cache(self.df1, "get_users")

        # Récupérer depuis le cache
        result = cache_module.get_from_cache("get_users")

        # Vérifier que les données sont identiques
        self.assertIsNotNone(result)
        pd.testing.assert_frame_equal(result, self.df1)

    def test_set_in_cache_with_parameters_and_get(self):
        """Test de stockage et récupération avec paramètres."""
        # Stocker dans le cache avec des paramètres
        cache_module.set_in_cache(self.df1, "get_users", "scope1", 100)

        # Récupérer avec les mêmes paramètres
        result = cache_module.get_from_cache("get_users", "scope1", 100)

        # Vérifier que les données sont identiques
        self.assertIsNotNone(result)
        pd.testing.assert_frame_equal(result, self.df1)

    def test_get_from_cache_returns_copy(self):
        """Test que get_from_cache retourne une copie profonde."""
        # Stocker dans le cache
        cache_module.set_in_cache(self.df1, "get_users")

        # Récupérer deux fois
        result1 = cache_module.get_from_cache("get_users")
        result2 = cache_module.get_from_cache("get_users")

        # Vérifier que ce sont des objets différents (copies)
        self.assertIsNot(result1, result2)

        # Mais avec les mêmes données
        pd.testing.assert_frame_equal(result1, result2)

        # Modifier une copie ne doit pas affecter l'autre
        result1.loc[0, 'name'] = 'Modified'
        self.assertNotEqual(result1.iloc[0]['name'], result2.iloc[0]['name'])

    def test_cache_isolation_different_keys(self):
        """Test que différentes clés sont isolées dans le cache."""
        # Stocker des données différentes avec des clés différentes
        cache_module.set_in_cache(self.df1, "get_users")
        cache_module.set_in_cache(self.df2, "get_companies")

        # Récupérer et vérifier l'isolation
        users = cache_module.get_from_cache("get_users")
        companies = cache_module.get_from_cache("get_companies")

        pd.testing.assert_frame_equal(users, self.df1)
        pd.testing.assert_frame_equal(companies, self.df2)

    def test_cache_isolation_different_parameters(self):
        """Test que différents paramètres sont isolés dans le cache."""
        # Stocker des données différentes avec des paramètres différents
        cache_module.set_in_cache(self.df1, "get_users", "scope1")
        cache_module.set_in_cache(self.df2, "get_users", "scope2")

        # Récupérer et vérifier l'isolation
        scope1_data = cache_module.get_from_cache("get_users", "scope1")
        scope2_data = cache_module.get_from_cache("get_users", "scope2")

        pd.testing.assert_frame_equal(scope1_data, self.df1)
        pd.testing.assert_frame_equal(scope2_data, self.df2)

    def test_invalidate_cache_key_existing(self):
        """Test d'invalidation d'une clé existante."""
        # Stocker dans le cache
        cache_module.set_in_cache(self.df1, "get_users")

        # Vérifier que c'est dans le cache
        result = cache_module.get_from_cache("get_users")
        self.assertIsNotNone(result)

        # Invalider la clé
        cache_module.invalidate_cache_key("get_users")

        # Vérifier que ce n'est plus dans le cache
        result = cache_module.get_from_cache("get_users")
        self.assertIsNone(result)

    def test_invalidate_cache_key_with_parameters(self):
        """Test d'invalidation d'une clé avec paramètres."""
        # Stocker dans le cache avec paramètres
        cache_module.set_in_cache(self.df1, "get_users", "scope1", 100)
        cache_module.set_in_cache(self.df2, "get_users", "scope2", 200)

        # Invalider une clé spécifique
        cache_module.invalidate_cache_key("get_users", "scope1", 100)

        # Vérifier que seule la clé spécifique a été invalidée
        result1 = cache_module.get_from_cache("get_users", "scope1", 100)
        result2 = cache_module.get_from_cache("get_users", "scope2", 200)

        self.assertIsNone(result1)
        self.assertIsNotNone(result2)
        pd.testing.assert_frame_equal(result2, self.df2)

    def test_invalidate_cache_key_nonexistent(self):
        """Test d'invalidation d'une clé inexistante (ne doit pas lever d'erreur)."""
        # Essayer d'invalider une clé qui n'existe pas
        cache_module.invalidate_cache_key("nonexistent_function")

        # Ne doit pas lever d'exception
        self.assertTrue(True)  # Le test passe s'il n'y a pas d'exception

    def test_clear_cache_empty(self):
        """Test de nettoyage d'un cache vide."""
        cache_module.clear_cache()

        # Vérifier que le cache est toujours vide
        result = cache_module.get_from_cache("get_users")
        self.assertIsNone(result)

    def test_clear_cache_with_data(self):
        """Test de nettoyage d'un cache avec des données."""
        # Stocker plusieurs éléments dans le cache
        cache_module.set_in_cache(self.df1, "get_users")
        cache_module.set_in_cache(self.df2, "get_companies")
        cache_module.set_in_cache(self.df_empty, "get_projects", "scope1")

        # Vérifier que les données sont dans le cache
        self.assertIsNotNone(cache_module.get_from_cache("get_users"))
        self.assertIsNotNone(cache_module.get_from_cache("get_companies"))
        self.assertIsNotNone(cache_module.get_from_cache("get_projects", "scope1"))

        # Nettoyer le cache
        cache_module.clear_cache()

        # Vérifier que tout a été supprimé
        self.assertIsNone(cache_module.get_from_cache("get_users"))
        self.assertIsNone(cache_module.get_from_cache("get_companies"))
        self.assertIsNone(cache_module.get_from_cache("get_projects", "scope1"))

    def test_cache_with_empty_dataframe(self):
        """Test de cache avec un DataFrame vide."""
        # Stocker un DataFrame vide
        cache_module.set_in_cache(self.df_empty, "get_empty")

        # Récupérer et vérifier
        result = cache_module.get_from_cache("get_empty")

        self.assertIsNotNone(result)
        self.assertTrue(result.empty)
        pd.testing.assert_frame_equal(result, self.df_empty)

    def test_cache_overwrite_existing_key(self):
        """Test d'écrasement d'une clé existante dans le cache."""
        # Stocker une première valeur
        cache_module.set_in_cache(self.df1, "get_users")

        # Vérifier la première valeur
        result1 = cache_module.get_from_cache("get_users")
        pd.testing.assert_frame_equal(result1, self.df1)

        # Écraser avec une nouvelle valeur
        cache_module.set_in_cache(self.df2, "get_users")

        # Vérifier la nouvelle valeur
        result2 = cache_module.get_from_cache("get_users")
        pd.testing.assert_frame_equal(result2, self.df2)

        # S'assurer que l'ancienne valeur n'est plus là
        self.assertFalse(result2.equals(self.df1))


if __name__ == '__main__':
    unittest.main()
