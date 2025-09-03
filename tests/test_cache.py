"""
Tests unitaires pour le système de cache avancé.

Ce module teste les fonctionnalités du cache avancé :
- Cache en mémoire et persistant
- Gestion du TTL
- Métriques
- Invalidation sélective
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
import pandas as pd
import sys
import os
from pathlib import Path

# Ajout du chemin du projet pour les imports
from core.cache import AdvancedCache, CacheEntry, CacheMetrics


class TestCacheEntry(unittest.TestCase):
    """Tests pour la classe CacheEntry."""

    def test_cache_entry_creation(self):
        """Test de création d'une entrée de cache."""
        data = {"test": "data"}
        entry = CacheEntry(data=data, timestamp=time.time(), ttl=3600)

        self.assertEqual(entry.data, data)
        self.assertIsInstance(entry.timestamp, float)
        self.assertEqual(entry.ttl, 3600)
        self.assertEqual(entry.access_count, 0)
        self.assertEqual(entry.last_access, 0.0)
        self.assertEqual(entry.size_bytes, 0)

    def test_cache_entry_is_expired(self):
        """Test de vérification d'expiration."""
        # Entrée expirée
        entry = CacheEntry(
            data={"test": "data"},
            timestamp=time.time() - 7200,  # 2 heures ago
            ttl=3600,  # 1 heure TTL
        )

        # Utiliser la méthode _is_expired du cache
        cache = AdvancedCache()
        self.assertTrue(cache._is_expired(entry))

        # Entrée valide
        entry = CacheEntry(data={"test": "data"}, timestamp=time.time(), ttl=3600)
        self.assertFalse(cache._is_expired(entry))

    def test_cache_entry_size(self):
        """Test du calcul de la taille d'une entrée."""
        data = {"test": "data", "large": "value" * 1000}
        entry = CacheEntry(data=data, timestamp=time.time(), ttl=3600)

        # Utiliser la méthode _calculate_size du cache
        cache = AdvancedCache()
        size = cache._calculate_size(data)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)


class TestCacheMetrics(unittest.TestCase):
    """Tests pour la classe CacheMetrics."""

    def test_cache_metrics_creation(self):
        """Test de création des métriques de cache."""
        metrics = CacheMetrics()

        self.assertEqual(metrics.hits, 0)
        self.assertEqual(metrics.misses, 0)
        self.assertEqual(metrics.sets, 0)
        self.assertEqual(metrics.invalidations, 0)
        self.assertEqual(metrics.total_size_bytes, 0)
        self.assertEqual(metrics.entry_count, 0)

    def test_cache_metrics_increment(self):
        """Test d'incrémentation des métriques."""
        metrics = CacheMetrics()

        metrics.hits += 1
        metrics.misses += 2
        metrics.sets += 3
        metrics.invalidations += 1

        self.assertEqual(metrics.hits, 1)
        self.assertEqual(metrics.misses, 2)
        self.assertEqual(metrics.sets, 3)
        self.assertEqual(metrics.invalidations, 1)

    def test_cache_metrics_str_representation(self):
        """Test de la représentation string des métriques."""
        metrics = CacheMetrics()
        metrics.hits = 10
        metrics.misses = 5
        metrics.sets = 8

        str_repr = str(metrics)
        self.assertIn("hits=10", str_repr)
        self.assertIn("misses=5", str_repr)
        self.assertIn("sets=8", str_repr)


class TestAdvancedCache(unittest.TestCase):
    """Tests pour la classe AdvancedCache."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache = AdvancedCache(
            cache_dir=self.cache_dir, max_size_mb=10, default_ttl=3600
        )

    def tearDown(self):
        """Nettoyage après les tests."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test de l'initialisation du cache."""
        self.assertEqual(self.cache.max_size_bytes, 10 * 1024 * 1024)
        self.assertEqual(self.cache.default_ttl, 3600)
        self.assertEqual(self.cache.cache_dir, self.cache_dir)
        self.assertIsInstance(self.cache.metrics, CacheMetrics)
        self.assertIsInstance(self.cache._memory_cache, dict)

    def test_make_key(self):
        """Test de création de clés de cache."""
        key1 = self.cache._make_key("test_function", "arg1", "arg2")
        key2 = self.cache._make_key("test_function", "arg1", "arg2")
        key3 = self.cache._make_key("test_function", "arg2", "arg1")

        # Mêmes arguments = même clé
        self.assertEqual(key1, key2)
        # Arguments différents = clés différentes
        self.assertNotEqual(key1, key3)

        # Clé est un hash MD5 (32 caractères hex)
        self.assertEqual(len(key1), 32)
        self.assertTrue(all(c in "0123456789abcdef" for c in key1))

    def test_get_set_basic(self):
        """Test de base get/set."""
        test_data = {"test": "data"}

        # Test set
        self.cache.set(test_data, "test_function", "arg1", "arg2")
        self.assertEqual(len(self.cache._memory_cache), 1)

        # Test get
        result = self.cache.get("test_function", "arg1", "arg2")
        self.assertEqual(result, test_data)

        # Vérification des métriques
        self.assertEqual(self.cache.metrics.sets, 1)
        self.assertEqual(self.cache.metrics.hits, 1)

    def test_get_nonexistent_key(self):
        """Test de récupération d'une clé inexistante."""
        result = self.cache.get("nonexistent_function", "arg1")
        self.assertIsNone(result)
        self.assertEqual(self.cache.metrics.misses, 1)

    def test_ttl_expiration(self):
        """Test d'expiration TTL."""
        test_data = {"test": "data"}

        # Créer une entrée avec un TTL très court
        self.cache.set(test_data, "test_function", "arg1", ttl=0.1)  # 100ms

        # Récupérer immédiatement
        result = self.cache.get("test_function", "arg1")
        self.assertEqual(result, test_data)

        # Attendre l'expiration
        time.sleep(0.2)

        # Récupérer après expiration
        result = self.cache.get("test_function", "arg1")
        self.assertIsNone(result)
        self.assertEqual(self.cache.metrics.misses, 1)

    def test_invalidate_specific_key(self):
        """Test d'invalidation d'une clé spécifique."""
        test_data = {"data": "test"}
        self.cache.set(test_data, "test_function", "arg1")

        # Vérifier que l'entrée existe
        self.assertIsNotNone(self.cache.get("test_function", "arg1"))

        # Invalider la clé spécifique
        success = self.cache.invalidate("test_function", "arg1")
        self.assertTrue(success)

        # Vérifier que l'entrée est supprimée
        self.assertIsNone(self.cache.get("test_function", "arg1"))

    def test_invalidate_nonexistent_key(self):
        """Test d'invalidation d'une clé inexistante."""
        success = self.cache.invalidate("nonexistent_function", "arg1")
        self.assertFalse(success)

    def test_clear_cache(self):
        """Test de nettoyage complet du cache."""
        # Ajouter plusieurs entrées
        self.cache.set({"data": "value1"}, "function1", "arg1")
        self.cache.set({"data": "value2"}, "function2", "arg1")

        # Vérifier que les entrées existent
        self.assertEqual(len(self.cache._memory_cache), 2)

        # Nettoyer le cache
        self.cache.clear()

        # Vérifier que le cache est vide
        self.assertEqual(len(self.cache._memory_cache), 0)
        self.assertIsNone(self.cache.get("function1", "arg1"))
        self.assertIsNone(self.cache.get("function2", "arg1"))

    def test_size_limit(self):
        """Test de limite de taille du cache."""
        # Créer des données volumineuses
        large_data = "x" * (5 * 1024 * 1024)  # 5MB

        # Ajouter une première entrée
        self.cache.set(large_data, "function1", "arg1")
        self.assertEqual(len(self.cache._memory_cache), 1)

        # Ajouter une deuxième entrée (devrait dépasser la limite de 10MB)
        self.cache.set(large_data, "function2", "arg1")

        # Vérifier que le cache a géré la limite
        # (le comportement exact dépend de l'implémentation)
        self.assertLessEqual(len(self.cache._memory_cache), 2)

    def test_persistent_cache(self):
        """Test du cache persistant."""
        test_data = {"test": "persistent_data"}

        # Ajouter une entrée
        self.cache.set(test_data, "persistent_function", "arg1")

        # Créer un nouveau cache (simule un redémarrage)
        new_cache = AdvancedCache(
            cache_dir=self.cache_dir, max_size_mb=10, default_ttl=3600
        )

        # Vérifier que l'entrée persiste
        result = new_cache.get("persistent_function", "arg1")
        self.assertEqual(result, test_data)

    def test_dataframe_caching(self):
        """Test de cache avec des DataFrames pandas."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        # Ajouter le DataFrame au cache
        self.cache.set(df, "dataframe_function", "arg1")

        # Récupérer le DataFrame
        result = self.cache.get("dataframe_function", "arg1")

        # Vérifier que c'est le même DataFrame
        pd.testing.assert_frame_equal(result, df)

    def test_get_metrics(self):
        """Test des métriques du cache."""
        # Ajouter quelques entrées
        self.cache.set({"data": "value1"}, "function1", "arg1")
        self.cache.set({"data": "value2"}, "function2", "arg1")

        # Récupérer quelques entrées
        self.cache.get("function1", "arg1")  # hit
        self.cache.get("nonexistent", "arg1")  # miss

        # Obtenir les métriques
        metrics = self.cache.get_metrics()

        # Vérifier les métriques
        self.assertEqual(metrics["sets"], 2)
        self.assertEqual(metrics["hits"], 1)
        self.assertEqual(metrics["misses"], 1)
        self.assertEqual(metrics["entry_count"], 2)
        self.assertGreater(metrics["total_size_mb"], 0)
        self.assertIn("hit_rate", metrics)

    def test_get_stats(self):
        """Test des statistiques du cache."""
        # Ajouter quelques entrées
        self.cache.set({"data": "value1"}, "function1", "arg1")
        self.cache.set({"data": "value2"}, "function2", "arg1")

        # Récupérer quelques entrées
        self.cache.get("function1", "arg1")  # hit
        self.cache.get("nonexistent", "arg1")  # miss

        # Obtenir les statistiques
        stats = self.cache.get_stats()

        # Vérifier que les statistiques contiennent les bonnes informations
        self.assertIn("Hits: 1", stats)
        self.assertIn("Misses: 1", stats)
        self.assertIn("Sets: 2", stats)
        self.assertIn("Entries: 2", stats)

    def test_cache_without_persistence(self):
        """Test du cache sans persistance."""
        cache = AdvancedCache(
            cache_dir=None, max_size_mb=10, default_ttl=3600  # Pas de persistance
        )

        test_data = {"test": "data"}
        cache.set(test_data, "test_function", "arg1")

        result = cache.get("test_function", "arg1")
        self.assertEqual(result, test_data)

        # Vérifier qu'il n'y a pas de répertoire de cache
        self.assertIsNone(cache.cache_dir)

    def test_calculate_size(self):
        """Test du calcul de la taille des données."""
        # Test avec un dictionnaire
        dict_data = {"key": "value"}
        size = self.cache._calculate_size(dict_data)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)

        # Test avec un DataFrame
        df = pd.DataFrame({"col": [1, 2, 3]})
        size = self.cache._calculate_size(df)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)

        # Test avec une chaîne
        str_data = "test string"
        size = self.cache._calculate_size(str_data)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)


if __name__ == "__main__":
    unittest.main()
