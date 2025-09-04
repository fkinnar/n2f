"""
Tests unitaires pour le module src/core/memory_manager.py.

Ce module teste le gestionnaire de mémoire intelligent pour les DataFrames.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import gc
import pandas as pd
import psutil

from core.memory_manager import (
    MemoryManager,
    DataFrameInfo,
    MemoryMetrics,
    get_memory_manager,
    register_dataframe,
    get_dataframe,
    cleanup_scope,
    cleanup_all,
    print_memory_summary,
    get_memory_stats,
)


class TestDataFrameInfo(unittest.TestCase):
    """Tests pour la classe DataFrameInfo."""

    def test_dataframe_info_creation(self):
        """Test de création d'un DataFrameInfo."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        info = DataFrameInfo(
            dataframe=df,
            size_mb=1.5,
            access_time=time.time(),
            scope="test",
            name="test_df",
        )

        self.assertEqual(info.dataframe.shape, (3, 2))
        self.assertEqual(info.size_mb, 1.5)
        self.assertEqual(info.scope, "test")
        self.assertEqual(info.name, "test_df")
        self.assertIsInstance(info.creation_time, float)


class TestMemoryMetrics(unittest.TestCase):
    """Tests pour la classe MemoryMetrics."""

    def test_memory_metrics_default_values(self):
        """Test des valeurs par défaut de MemoryMetrics."""
        metrics = MemoryMetrics()

        self.assertEqual(metrics.current_usage_mb, 0.0)
        self.assertEqual(metrics.peak_usage_mb, 0.0)
        self.assertEqual(metrics.total_dataframes, 0)
        self.assertEqual(metrics.freed_memory_mb, 0.0)
        self.assertEqual(metrics.cleanup_count, 0)
        self.assertEqual(metrics.last_cleanup_time, 0.0)


class TestMemoryManager(unittest.TestCase):
    """Tests pour la classe MemoryManager."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Mock psutil.Process pour éviter les appels système
        self.process_patcher = patch("core.memory_manager.psutil.Process")
        self.mock_process = self.process_patcher.start()
        self.mock_process_instance = Mock()
        self.mock_process.return_value = self.mock_process_instance

        # Mock psutil.virtual_memory
        self.virtual_memory_patcher = patch("core.memory_manager.psutil.virtual_memory")
        self.mock_virtual_memory = self.virtual_memory_patcher.start()

        # Mock print pour éviter l'affichage
        self.print_patcher = patch("logging.info")
        self.mock_print = self.print_patcher.start()

        self.memory_manager = MemoryManager(max_memory_mb=100, cleanup_threshold=0.8)

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.process_patcher.stop()
        self.virtual_memory_patcher.stop()
        self.print_patcher.stop()

    def test_memory_manager_initialization(self):
        """Test de l'initialisation du MemoryManager."""
        self.assertEqual(self.memory_manager.max_memory_mb, 100)
        self.assertEqual(self.memory_manager.cleanup_threshold, 0.8)
        self.assertEqual(len(self.memory_manager.dataframes), 0)
        self.assertIsInstance(self.memory_manager.metrics, MemoryMetrics)

    def test_calculate_dataframe_size(self):
        """Test du calcul de la taille d'un DataFrame."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        size = self.memory_manager._calculate_dataframe_size(df)
        self.assertIsInstance(size, float)
        self.assertGreater(size, 0)

    def test_register_dataframe_success(self):
        """Test d'enregistrement réussi d'un DataFrame."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        result = self.memory_manager.register_dataframe("test_df", df, "test_scope")

        self.assertTrue(result)
        self.assertIn("test_df", self.memory_manager.dataframes)
        self.assertEqual(self.memory_manager.dataframes["test_df"].scope, "test_scope")
        self.assertEqual(self.memory_manager.dataframes["test_df"].name, "test_df")

    def test_register_dataframe_insufficient_memory(self):
        """Test d'enregistrement avec mémoire insuffisante."""
        # Créer un DataFrame qui dépasse la limite
        large_df = pd.DataFrame({"col1": range(10000), "col2": ["x"] * 10000})

        # Mock _calculate_dataframe_size pour retourner une grande taille
        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=200.0
        ):
            result = self.memory_manager.register_dataframe(
                "large_df", large_df, "test_scope"
            )

        self.assertFalse(result)
        self.assertNotIn("large_df", self.memory_manager.dataframes)

    def test_register_dataframe_triggers_cleanup(self):
        """Test que l'enregistrement déclenche le nettoyage si nécessaire."""
        # Créer plusieurs DataFrames pour atteindre le seuil
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})

        # Mock _calculate_dataframe_size pour contrôler les tailles
        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=50.0
        ):
            # Premier DataFrame
            result1 = self.memory_manager.register_dataframe("df1", df1, "scope1")
            self.assertTrue(result1)

            # Deuxième DataFrame devrait déclencher le nettoyage
            with patch.object(self.memory_manager, "_cleanup_oldest") as mock_cleanup:
                result2 = self.memory_manager.register_dataframe("df2", df2, "scope2")
                mock_cleanup.assert_called_once()

    def test_get_dataframe_success(self):
        """Test de récupération réussie d'un DataFrame."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        self.memory_manager.register_dataframe("test_df", df, "test_scope")

        # Mock time.time pour contrôler le temps d'accès
        with patch("time.time", return_value=1234567890.0):
            result = self.memory_manager.get_dataframe("test_df")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(
            self.memory_manager.dataframes["test_df"].access_time, 1234567890.0
        )

    def test_get_dataframe_not_found(self):
        """Test de récupération d'un DataFrame inexistant."""
        result = self.memory_manager.get_dataframe("nonexistent_df")
        self.assertIsNone(result)

    def test_cleanup_scope(self):
        """Test du nettoyage d'un scope spécifique."""
        # Créer des DataFrames dans différents scopes
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})
        df3 = pd.DataFrame({"col3": [7, 8, 9]})

        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=10.0
        ):
            self.memory_manager.register_dataframe("df1", df1, "scope1")
            self.memory_manager.register_dataframe("df2", df2, "scope1")
            self.memory_manager.register_dataframe("df3", df3, "scope2")

            # Nettoyer scope1
            freed_memory = self.memory_manager.cleanup_scope("scope1")

            self.assertEqual(freed_memory, 20.0)  # 2 DataFrames * 10.0 MB
            self.assertNotIn("df1", self.memory_manager.dataframes)
            self.assertNotIn("df2", self.memory_manager.dataframes)
            self.assertIn("df3", self.memory_manager.dataframes)

    def test_cleanup_scope_empty(self):
        """Test du nettoyage d'un scope vide."""
        freed_memory = self.memory_manager.cleanup_scope("empty_scope")
        self.assertEqual(freed_memory, 0.0)

    def test_cleanup_all(self):
        """Test du nettoyage complet."""
        # Créer des DataFrames
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})

        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=15.0
        ):
            self.memory_manager.register_dataframe("df1", df1, "scope1")
            self.memory_manager.register_dataframe("df2", df2, "scope2")

            # Nettoyer tout
            freed_memory = self.memory_manager.cleanup_all()

            self.assertEqual(freed_memory, 30.0)  # 2 DataFrames * 15.0 MB
            self.assertEqual(len(self.memory_manager.dataframes), 0)
            self.assertEqual(self.memory_manager.metrics.current_usage_mb, 0.0)

    def test_cleanup_oldest(self):
        """Test du nettoyage des plus anciens DataFrames."""
        # Créer plusieurs DataFrames
        dfs = []
        for i in range(5):
            df = pd.DataFrame({"col": range(i * 1000)})
            dfs.append(df)

        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=20.0
        ):
            for i, df in enumerate(dfs):
                self.memory_manager.register_dataframe(f"df{i}", df, f"scope{i}")

            # Forcer le nettoyage
            self.memory_manager._cleanup_oldest()

            # Vérifier que certains DataFrames ont été supprimés
            self.assertLess(len(self.memory_manager.dataframes), 5)

    def test_cleanup_oldest_empty(self):
        """Test du nettoyage avec aucun DataFrame."""
        self.memory_manager._cleanup_oldest()
        # Ne devrait pas lever d'exception

    def test_get_dataframes_by_scope(self):
        """Test du groupement des DataFrames par scope."""
        # Créer des DataFrames dans différents scopes
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})
        df3 = pd.DataFrame({"col3": [7, 8, 9]})

        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=10.0
        ):
            self.memory_manager.register_dataframe("df1", df1, "scope1")
            self.memory_manager.register_dataframe("df2", df2, "scope1")
            self.memory_manager.register_dataframe("df3", df3, "scope2")

            result = self.memory_manager._get_dataframes_by_scope()

            self.assertIn("scope1", result)
            self.assertIn("scope2", result)
            self.assertEqual(result["scope1"]["count"], 2)
            self.assertEqual(result["scope1"]["size_mb"], 20.0)
            self.assertEqual(result["scope2"]["count"], 1)
            self.assertEqual(result["scope2"]["size_mb"], 10.0)

    def test_get_memory_stats(self):
        """Test de l'obtention des statistiques mémoire."""
        # Mock psutil.virtual_memory
        mock_vm = Mock()
        mock_vm.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_vm.percent = 50.0
        self.mock_virtual_memory.return_value = mock_vm

        # Mock process.memory_info
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        self.mock_process_instance.memory_info.return_value = mock_memory_info

        # Créer un DataFrame
        df = pd.DataFrame({"col1": [1, 2, 3]})
        with patch.object(
            self.memory_manager, "_calculate_dataframe_size", return_value=5.0
        ):
            self.memory_manager.register_dataframe("test_df", df, "test_scope")

            stats = self.memory_manager.get_memory_stats()

            self.assertIn("memory_manager", stats)
            self.assertIn("system", stats)
            self.assertIn("dataframes_by_scope", stats)

            mm_stats = stats["memory_manager"]
            self.assertEqual(mm_stats["current_usage_mb"], 5.0)
            self.assertEqual(mm_stats["max_memory_mb"], 100)
            self.assertEqual(mm_stats["total_dataframes"], 1)
            self.assertEqual(mm_stats["active_dataframes"], 1)

    def test_print_memory_summary(self):
        """Test de l'affichage du résumé mémoire."""
        # Mock get_memory_stats
        mock_stats = {
            "memory_manager": {
                "current_usage_mb": 25.5,
                "peak_usage_mb": 50.0,
                "max_memory_mb": 100,
                "usage_percentage": 25.5,
                "total_dataframes": 3,
                "active_dataframes": 2,
                "freed_memory_mb": 15.0,
                "cleanup_count": 1,
            },
            "system": {"memory_percentage": 60.0, "process_memory_mb": 75.0},
            "dataframes_by_scope": {
                "scope1": {"count": 1, "size_mb": 15.0},
                "scope2": {"count": 1, "size_mb": 10.5},
            },
        }

        with patch.object(
            self.memory_manager, "get_memory_stats", return_value=mock_stats
        ):
            self.memory_manager.print_memory_summary()

            # Vérifier que print a été appelé plusieurs fois
            self.assertGreater(self.mock_print.call_count, 5)


class TestGlobalFunctions(unittest.TestCase):
    """Tests pour les fonctions globales du module."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Reset l'instance globale
        import core.memory_manager

        core.memory_manager._memory_manager = None

        # Mock psutil
        self.process_patcher = patch("core.memory_manager.psutil.Process")
        self.mock_process = self.process_patcher.start()
        self.mock_process_instance = Mock()
        self.mock_process.return_value = self.mock_process_instance

        self.virtual_memory_patcher = patch("core.memory_manager.psutil.virtual_memory")
        self.mock_virtual_memory = self.virtual_memory_patcher.start()

        self.print_patcher = patch("logging.info")
        self.mock_print = self.print_patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.process_patcher.stop()
        self.virtual_memory_patcher.stop()
        self.print_patcher.stop()

    def test_get_memory_manager_singleton(self):
        """Test que get_memory_manager retourne toujours la même instance."""
        manager1 = get_memory_manager(max_memory_mb=200)
        manager2 = get_memory_manager(max_memory_mb=300)  # Paramètre ignoré

        self.assertIs(manager1, manager2)
        self.assertEqual(manager1.max_memory_mb, 200)  # Première valeur conservée

    def test_register_dataframe_global(self):
        """Test de la fonction globale register_dataframe."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        result = register_dataframe("test_df", df, "test_scope")
        self.assertTrue(result)

    def test_get_dataframe_global(self):
        """Test de la fonction globale get_dataframe."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        register_dataframe("test_df", df, "test_scope")

        result = get_dataframe("test_df")
        self.assertIsInstance(result, pd.DataFrame)

    def test_cleanup_scope_global(self):
        """Test de la fonction globale cleanup_scope."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        register_dataframe("test_df", df, "test_scope")

        freed_memory = cleanup_scope("test_scope")
        self.assertGreater(freed_memory, 0)

    def test_cleanup_all_global(self):
        """Test de la fonction globale cleanup_all."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        register_dataframe("test_df", df, "test_scope")

        freed_memory = cleanup_all()
        self.assertGreater(freed_memory, 0)

    def test_print_memory_summary_global(self):
        """Test de la fonction globale print_memory_summary."""
        # Mock psutil.virtual_memory
        mock_vm = Mock()
        mock_vm.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_vm.percent = 50.0
        self.mock_virtual_memory.return_value = mock_vm

        # Mock process.memory_info
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        self.mock_process_instance.memory_info.return_value = mock_memory_info

        print_memory_summary()
        # Vérifier que print a été appelé
        self.assertGreater(self.mock_print.call_count, 0)

    def test_get_memory_stats_global(self):
        """Test de la fonction globale get_memory_stats."""
        # Mock psutil.virtual_memory
        mock_vm = Mock()
        mock_vm.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_vm.percent = 50.0
        self.mock_virtual_memory.return_value = mock_vm

        # Mock process.memory_info
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        self.mock_process_instance.memory_info.return_value = mock_memory_info

        stats = get_memory_stats()
        self.assertIn("memory_manager", stats)
        self.assertIn("system", stats)
        self.assertIn("dataframes_by_scope", stats)


if __name__ == "__main__":
    unittest.main()
