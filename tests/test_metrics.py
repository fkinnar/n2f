"""
Tests unitaires pour le système de métriques.

Ce module teste les fonctionnalités du système de métriques :
- Métriques d'opérations
- Métriques de scope
- Export et résumé
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
import json
import sys
import os
from pathlib import Path

# Ajout du chemin du projet pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from core.metrics import SyncMetrics, OperationMetrics, ScopeMetrics


class TestOperationMetrics(unittest.TestCase):
    """Tests pour la classe OperationMetrics."""

    def test_operation_metrics_creation(self):
        """Test de création des métriques d'opération."""
        with patch('time.time', return_value=100.0):
            metrics = OperationMetrics(
                scope="test_scope",
                action="create",
                start_time=100.0
            )

        self.assertEqual(metrics.scope, "test_scope")
        self.assertEqual(metrics.action, "create")
        self.assertEqual(metrics.start_time, 100.0)
        self.assertIsNone(metrics.end_time)
        self.assertTrue(metrics.success)
        self.assertEqual(metrics.records_processed, 0)
        self.assertEqual(metrics.memory_usage_mb, 0.0)
        self.assertEqual(metrics.api_calls, 0)
        self.assertEqual(metrics.cache_hits, 0)
        self.assertEqual(metrics.cache_misses, 0)

    def test_duration_seconds(self):
        """Test du calcul de la durée."""
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.5]  # start, end
            metrics = OperationMetrics(
                scope="test_scope",
                action="create",
                start_time=100.0
            )
            metrics.end_time = 102.5

        self.assertEqual(metrics.duration_seconds, 2.5)

    def test_duration_seconds_without_end_time(self):
        """Test du calcul de la durée sans end_time."""
        metrics = OperationMetrics(
            scope="test_scope",
            action="create",
            start_time=100.0
        )

        # Le calcul de la durée utilise time.time() directement dans la propriété
        # On ne peut pas facilement mocker cela, donc on teste juste que la propriété fonctionne
        duration = metrics.duration_seconds
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 0)

    def test_records_per_second(self):
        """Test du calcul des enregistrements par seconde."""
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0]  # start, end
            metrics = OperationMetrics(
                scope="test_scope",
                action="create",
                start_time=100.0
            )
            metrics.end_time = 102.0
            metrics.records_processed = 100

        self.assertEqual(metrics.records_per_second, 50.0)  # 100 records / 2 seconds

    def test_records_per_second_zero_duration(self):
        """Test du calcul avec durée zéro."""
        metrics = OperationMetrics(
            scope="test_scope",
            action="create",
            start_time=100.0
        )
        metrics.end_time = 100.0  # Même temps
        metrics.records_processed = 100

        self.assertEqual(metrics.records_per_second, 0.0)

    def test_to_dict(self):
        """Test de conversion en dictionnaire."""
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0]  # start, end
            metrics = OperationMetrics(
                scope="test_scope",
                action="create",
                start_time=100.0
            )
            metrics.end_time = 102.0
            metrics.success = True
            metrics.records_processed = 50
            metrics.memory_usage_mb = 10.5
            metrics.api_calls = 5
            metrics.cache_hits = 3
            metrics.cache_misses = 2

        data = metrics.to_dict()

        self.assertEqual(data['scope'], "test_scope")
        self.assertEqual(data['action'], "create")
        self.assertEqual(data['start_time'], 100.0)
        self.assertEqual(data['end_time'], 102.0)
        self.assertEqual(data['duration_seconds'], 2.0)
        self.assertTrue(data['success'])
        self.assertEqual(data['records_processed'], 50)
        self.assertEqual(data['records_per_second'], 25.0)
        self.assertEqual(data['memory_usage_mb'], 10.5)
        self.assertEqual(data['api_calls'], 5)
        self.assertEqual(data['cache_hits'], 3)
        self.assertEqual(data['cache_misses'], 2)


class TestScopeMetrics(unittest.TestCase):
    """Tests pour la classe ScopeMetrics."""

    def test_scope_metrics_creation(self):
        """Test de création des métriques de scope."""
        metrics = ScopeMetrics("test_scope")

        self.assertEqual(metrics.scope, "test_scope")
        self.assertEqual(metrics.total_operations, 0)
        self.assertEqual(metrics.successful_operations, 0)
        self.assertEqual(metrics.failed_operations, 0)
        self.assertEqual(metrics.total_duration_seconds, 0.0)
        self.assertEqual(metrics.total_records_processed, 0)
        self.assertEqual(metrics.peak_memory_usage_mb, 0.0)
        self.assertEqual(metrics.total_api_calls, 0)
        self.assertEqual(metrics.total_cache_hits, 0)
        self.assertEqual(metrics.total_cache_misses, 0)
        self.assertEqual(metrics.operations_by_action, {})

    def test_success_rate(self):
        """Test du calcul du taux de succès."""
        metrics = ScopeMetrics("test_scope")

        # Aucune opération
        self.assertEqual(metrics.success_rate, 0.0)

        # Quelques opérations
        metrics.total_operations = 10
        metrics.successful_operations = 8
        metrics.failed_operations = 2

        self.assertEqual(metrics.success_rate, 0.8)

    def test_average_duration_seconds(self):
        """Test du calcul de la durée moyenne."""
        metrics = ScopeMetrics("test_scope")

        # Aucune opération
        self.assertEqual(metrics.average_duration_seconds, 0.0)

        # Quelques opérations
        metrics.total_operations = 4
        metrics.total_duration_seconds = 10.0

        self.assertEqual(metrics.average_duration_seconds, 2.5)

    def test_cache_hit_rate(self):
        """Test du calcul du taux de hit du cache."""
        metrics = ScopeMetrics("test_scope")

        # Aucune opération de cache
        self.assertEqual(metrics.cache_hit_rate, 0.0)

        # Quelques opérations de cache
        metrics.total_cache_hits = 8
        metrics.total_cache_misses = 2

        self.assertEqual(metrics.cache_hit_rate, 0.8)

    def test_to_dict(self):
        """Test de conversion en dictionnaire."""
        metrics = ScopeMetrics("test_scope")
        metrics.total_operations = 10
        metrics.successful_operations = 8
        metrics.failed_operations = 2
        metrics.total_duration_seconds = 20.0
        metrics.total_records_processed = 100
        metrics.peak_memory_usage_mb = 50.0
        metrics.total_api_calls = 25
        metrics.total_cache_hits = 15
        metrics.total_cache_misses = 5
        metrics.operations_by_action = {"create": 5, "update": 3, "delete": 2}

        data = metrics.to_dict()

        self.assertEqual(data['scope'], "test_scope")
        self.assertEqual(data['total_operations'], 10)
        self.assertEqual(data['successful_operations'], 8)
        self.assertEqual(data['failed_operations'], 2)
        self.assertEqual(data['success_rate'], 0.8)
        self.assertEqual(data['total_duration_seconds'], 20.0)
        self.assertEqual(data['average_duration_seconds'], 2.0)
        self.assertEqual(data['total_records_processed'], 100)
        self.assertEqual(data['peak_memory_usage_mb'], 50.0)
        self.assertEqual(data['total_api_calls'], 25)
        self.assertEqual(data['cache_hit_rate'], 0.75)
        self.assertEqual(data['total_cache_hits'], 15)
        self.assertEqual(data['total_cache_misses'], 5)
        self.assertEqual(data['operations_by_action'], {"create": 5, "update": 3, "delete": 2})


class TestSyncMetrics(unittest.TestCase):
    """Tests pour la classe SyncMetrics."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.metrics = SyncMetrics()

    def test_initialization(self):
        """Test de l'initialisation du système de métriques."""
        self.assertIsInstance(self.metrics.operations, list)
        self.assertIsInstance(self.metrics.memory_usage_history, list)
        self.assertIsInstance(self.metrics.error_history, list)
        self.assertIsInstance(self.metrics.api_call_history, list)
        self.assertIsInstance(self.metrics.start_time, float)

    def test_start_operation(self):
        """Test de démarrage d'une opération."""
        with patch('time.time', return_value=100.0):
            op_metrics = self.metrics.start_operation("test_scope", "create")

        self.assertIsInstance(op_metrics, OperationMetrics)
        self.assertEqual(op_metrics.scope, "test_scope")
        self.assertEqual(op_metrics.action, "create")
        self.assertEqual(op_metrics.start_time, 100.0)
        self.assertEqual(len(self.metrics.operations), 1)
        self.assertIn(op_metrics, self.metrics.operations)

    def test_end_operation(self):
        """Test de fin d'une opération."""
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0, 102.0]  # start, end, end_operation
            op_metrics = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(
                op_metrics,
                success=True,
                records_processed=50,
                memory_usage_mb=10.5,
                api_calls=5,
                cache_hits=3,
                cache_misses=2
            )

        self.assertEqual(op_metrics.end_time, 102.0)
        self.assertTrue(op_metrics.success)
        self.assertEqual(op_metrics.records_processed, 50)
        self.assertEqual(op_metrics.memory_usage_mb, 10.5)
        self.assertEqual(op_metrics.api_calls, 5)
        self.assertEqual(op_metrics.cache_hits, 3)
        self.assertEqual(op_metrics.cache_misses, 2)

    def test_end_operation_with_error(self):
        """Test de fin d'une opération avec erreur."""
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 101.0, 101.0]  # start, end, end_operation
            op_metrics = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(
                op_metrics,
                success=False,
                error_message="Test error",
                records_processed=0
            )

        self.assertFalse(op_metrics.success)
        self.assertEqual(op_metrics.error_message, "Test error")
        self.assertEqual(len(self.metrics.error_history), 1)
        self.assertEqual(self.metrics.error_history[0]['error_message'], "Test error")

    def test_record_memory_usage(self):
        """Test d'enregistrement de l'utilisation mémoire."""
        self.metrics.record_memory_usage(1024.0, "test_scope")

        self.assertEqual(len(self.metrics.memory_usage_history), 1)
        self.assertEqual(self.metrics.memory_usage_history[0]['usage_mb'], 1024.0)
        self.assertEqual(self.metrics.memory_usage_history[0]['scope'], "test_scope")

    def test_get_scope_metrics(self):
        """Test de récupération des métriques de scope."""
        # Créer quelques opérations
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0, 103.0, 105.0, 105.0]  # start1, end1, start2, end2, end_operation
            op1 = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(op1, success=True, records_processed=50)

            op2 = self.metrics.start_operation("test_scope", "update")
            self.metrics.end_operation(op2, success=False, records_processed=25)

        scope_metrics = self.metrics.get_scope_metrics("test_scope")

        self.assertEqual(scope_metrics.scope, "test_scope")
        self.assertEqual(scope_metrics.total_operations, 2)
        self.assertEqual(scope_metrics.successful_operations, 1)
        self.assertEqual(scope_metrics.failed_operations, 1)
        self.assertEqual(scope_metrics.total_records_processed, 75)
        self.assertEqual(scope_metrics.success_rate, 0.5)

    def test_get_summary(self):
        """Test de génération du résumé."""
        # Créer quelques opérations
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0, 103.0, 105.0, 105.0]  # start1, end1, start2, end2, end_operation
            op1 = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(op1, success=True, records_processed=50)

            op2 = self.metrics.start_operation("test_scope", "update")
            self.metrics.end_operation(op2, success=False, records_processed=25)

        summary = self.metrics.get_summary()

        # Vérifier que le résumé contient les bonnes informations
        self.assertIn("summary", summary)
        self.assertIn("performance", summary)
        self.assertIn("memory", summary)
        self.assertIn("operations_by_scope", summary)
        self.assertIn("operations_by_action", summary)
        self.assertEqual(summary["summary"]["total_operations"], 2)
        self.assertEqual(summary["summary"]["successful_operations"], 1)
        self.assertEqual(summary["summary"]["failed_operations"], 1)

    def test_export_metrics(self):
        """Test d'export des métriques."""
        # Créer quelques opérations
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0, 102.0]  # start, end, end_operation
            op_metrics = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(op_metrics, success=True, records_processed=50)

        # Exporter vers un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            self.metrics.export_metrics(filename)

            # Vérifier que le fichier a été créé et contient des données JSON
            with open(filename, 'r') as f:
                data = json.load(f)

            self.assertIn("operations", data)
            self.assertIn("summary", data)
            self.assertIn("memory_history", data)
            self.assertIn("error_history", data)

        finally:
            # Nettoyer le fichier temporaire
            os.unlink(filename)

    def test_print_summary(self):
        """Test d'affichage du résumé."""
        # Créer quelques opérations
        with patch('time.time') as mock_time:
            mock_time.side_effect = [100.0, 102.0, 102.0]  # start, end, end_operation
            op_metrics = self.metrics.start_operation("test_scope", "create")
            self.metrics.end_operation(op_metrics, success=True, records_processed=50)

        # Test que la méthode ne lève pas d'exception
        try:
            self.metrics.print_summary()
        except Exception as e:
            self.fail(f"print_summary() a levé une exception: {e}")


if __name__ == '__main__':
    unittest.main()
